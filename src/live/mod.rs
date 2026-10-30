mod announce;
mod feed;
mod routes;
mod schedule;
mod timers;

use anyhow::Result;
use chrono::{DateTime, NaiveDate, NaiveDateTime, TimeDelta, Utc};
use model::first::{
    ApiClient, ApiParams, EventCode, EventSummary, EventsResponse, ScheduleResponse, alliance_teams,
};
use model::prelude::Supabase;
use serenity::all::{ChannelId, GuildId, Http};
use std::collections::{BTreeSet, HashMap, HashSet};
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::{Mutex, mpsc};
use tokio::task::JoinSet;
use tokio::time::MissedTickBehavior;

use crate::favorites::FavoritesManager;
use crate::services::Services;
use crate::subscriptions::Subscriptions;
use crate::team_store::TeamStore;
use announce::Card;
use feed::{Feed, Fresh, Polled};
use routes::Routes;
use schedule::{EventWindow, Phase};
use timers::Timers;

const LIVE_INTERVAL: TimeDelta = TimeDelta::seconds(20);
const IDLE_INTERVAL: TimeDelta = TimeDelta::seconds(60);
/// An event counts as live this long after its last posted result.
const LIVE_WINDOW: TimeDelta = TimeDelta::minutes(15);
/// Caps each sleep so wall-clock jumps are noticed.
const MAX_SLEEP: Duration = Duration::from_secs(60 * 60);
const REFRESH: Duration = Duration::from_secs(6 * 60 * 60);
const LOAD_RETRY: Duration = Duration::from_secs(60);

pub enum RouteChange {
    Subscribed {
        guild: GuildId,
        channel: ChannelId,
        event: EventSummary,
    },
    Unsubscribed {
        guild: GuildId,
        code: EventCode,
    },
    Favorited {
        guild: GuildId,
        channel: ChannelId,
        team: u32,
    },
    Unfavorited {
        guild: GuildId,
        team: u32,
    },
}

#[derive(Clone)]
pub struct LiveHandle(mpsc::UnboundedSender<RouteChange>);

impl LiveHandle {
    pub fn channel() -> (Self, mpsc::UnboundedReceiver<RouteChange>) {
        let (tx, rx) = mpsc::unbounded_channel();
        (Self(tx), rx)
    }

    /// A no-op when live cards are disabled.
    pub fn send(&self, change: RouteChange) {
        let _ = self.0.send(change);
    }
}

struct Shared {
    first: ApiClient,
    db: Supabase,
    teams: Arc<TeamStore>,
    http: Arc<Http>,
    season: i32,
}

impl Shared {
    fn params<'a>(&self, path: impl IntoIterator<Item = &'a str>) -> ApiParams {
        let mut segments = vec![self.season.to_string()];
        segments.extend(path.into_iter().map(str::to_owned));
        ApiParams::new(segments)
    }

    async fn events(&self, key: &str, value: String) -> Result<Vec<EventSummary>> {
        let params = self.params(["events"]).with_query(key, value);
        Ok(self.first.get::<EventsResponse>(&params).await?.events)
    }

    async fn schedule(&self, code: &EventCode) -> Result<Vec<NaiveDateTime>> {
        let params = self
            .params(["schedule", code.as_str()])
            .with_query("tournamentLevel", "qual");
        let resp: ScheduleResponse = self.first.get(&params).await?;
        Ok(resp
            .schedule
            .into_iter()
            .filter_map(|m| m.start_time)
            .collect())
    }
}

#[derive(Default)]
struct Tracked {
    /// Locked while a poll is in flight.
    feed: Arc<Mutex<Feed>>,
    warmed: Option<NaiveDate>,
    last_result: Option<DateTime<Utc>>,
}

enum Done {
    TeamEvents {
        team: u32,
        events: Result<Vec<EventSummary>>,
    },
    Event {
        code: EventCode,
        event: Result<Option<EventSummary>>,
    },
    Schedule {
        code: EventCode,
        day: NaiveDate,
        starts: Result<Vec<NaiveDateTime>>,
    },
    Polled {
        code: EventCode,
        polled: Result<Polled>,
    },
    Posted {
        gone: BTreeSet<ChannelId>,
    },
    Saved {
        what: &'static str,
        saved: Result<()>,
    },
}

/// Follows subscribed events and favorite teams' events, sleeping until each one opens.
pub struct Live {
    shared: Arc<Shared>,
    favorites: Arc<FavoritesManager>,
    subscriptions: Arc<Subscriptions>,
    inbox: mpsc::UnboundedReceiver<RouteChange>,
    routes: Routes,
    windows: HashMap<EventCode, EventWindow>,
    team_events: HashMap<u32, Vec<EventCode>>,
    tracked: HashMap<EventCode, Tracked>,
    timers: Timers<EventCode>,
    tasks: JoinSet<Done>,
}

impl Live {
    pub fn new(
        services: &Services,
        first: ApiClient,
        db: Supabase,
        http: Arc<Http>,
        inbox: mpsc::UnboundedReceiver<RouteChange>,
    ) -> Self {
        Self {
            shared: Arc::new(Shared {
                first,
                db,
                teams: services.teams.clone(),
                http,
                season: services.season,
            }),
            favorites: services.favorites.clone(),
            subscriptions: services.subscriptions.clone(),
            inbox,
            routes: Routes::default(),
            windows: HashMap::new(),
            team_events: HashMap::new(),
            tracked: HashMap::new(),
            timers: Timers::default(),
            tasks: JoinSet::new(),
        }
    }

    pub async fn run(mut self) {
        self.load_routes().await;
        let mut refresh = tokio::time::interval(REFRESH);
        refresh.set_missed_tick_behavior(MissedTickBehavior::Delay);

        loop {
            let sleep = self.timers.next().map_or(MAX_SLEEP, |at| {
                (at - Utc::now())
                    .to_std()
                    .unwrap_or_default()
                    .min(MAX_SLEEP)
            });
            tokio::select! {
                Some(change) = self.inbox.recv() => self.apply(change),
                Some(done) = self.tasks.join_next() => match done {
                    Ok(done) => self.finish(done),
                    Err(err) => {
                        tracing::error!(error = %err, "Live match task failed");
                        self.rearm();
                    }
                },
                _ = refresh.tick() => self.refresh(),
                () = tokio::time::sleep(sleep) => {}
            }
            for code in self.timers.pop_due(Utc::now()) {
                self.wake(code);
            }
        }
    }

    async fn load_routes(&mut self) {
        loop {
            match tokio::try_join!(self.subscriptions.all(), self.favorites.announced()) {
                Ok((subscriptions, favorites)) => {
                    for (guild, code, channel) in subscriptions {
                        self.routes.events.follow(code, guild, channel);
                    }
                    for (guild, team, channel) in favorites {
                        self.routes.teams.follow(team, guild, channel);
                    }
                    tracing::info!(
                        events = self.routes.events.keys().count(),
                        teams = self.routes.teams.keys().count(),
                        "Live match routes loaded"
                    );
                    return;
                }
                Err(err) => {
                    tracing::warn!(error = %err, "Could not load live match routes; retrying");
                    tokio::time::sleep(LOAD_RETRY).await;
                }
            }
        }
    }

    /// Picks up events teams registered for since the last look.
    fn refresh(&mut self) {
        let teams: Vec<u32> = self.routes.teams.keys().copied().collect();
        for team in teams {
            self.lookup_team(team);
        }
        let unknown: Vec<EventCode> = self
            .routes
            .events
            .keys()
            .filter(|code| !self.windows.contains_key(*code))
            .cloned()
            .collect();
        for code in unknown {
            self.lookup_event(code);
        }
    }

    fn apply(&mut self, change: RouteChange) {
        match change {
            RouteChange::Subscribed {
                guild,
                channel,
                event,
            } => {
                let Some(code) = event.code.clone() else {
                    return;
                };
                if let Some(window) = EventWindow::from_summary(&event) {
                    self.windows.insert(code.clone(), window);
                }
                self.routes.events.follow(code, guild, channel);
            }
            RouteChange::Unsubscribed { guild, code } => self.routes.events.unfollow(&code, guild),
            RouteChange::Favorited {
                guild,
                channel,
                team,
            } => {
                if !self.routes.teams.contains(&team) {
                    self.lookup_team(team);
                }
                self.routes.teams.follow(team, guild, channel);
            }
            RouteChange::Unfavorited { guild, team } => self.routes.teams.unfollow(&team, guild),
        }
        self.reconcile();
    }

    fn finish(&mut self, done: Done) {
        match done {
            Done::TeamEvents { team, events } => match events {
                Ok(events) => {
                    let codes = events
                        .into_iter()
                        .filter(|e| e.type_name.has_matches())
                        .filter_map(|e| {
                            let code = e.code.clone()?;
                            self.windows
                                .insert(code.clone(), EventWindow::from_summary(&e)?);
                            Some(code)
                        })
                        .collect();
                    self.team_events.insert(team, codes);
                    self.reconcile();
                }
                Err(err) => tracing::warn!(team, error = %err, "Could not list team events"),
            },
            Done::Event { code, event } => match event {
                Ok(Some(event)) => {
                    if let Some(window) = EventWindow::from_summary(&event) {
                        self.windows.insert(code, window);
                        self.reconcile();
                    }
                }
                Ok(None) => tracing::warn!(event = %code, "Subscribed event no longer exists"),
                Err(err) => tracing::warn!(event = %code, error = %err, "Could not look up event"),
            },
            Done::Schedule { code, day, starts } => {
                let warm_up = match starts {
                    Ok(starts) => self.windows.get(&code).and_then(|w| w.warm_up(day, starts)),
                    Err(err) => {
                        tracing::warn!(event = %code, error = %err, "Could not read match schedule");
                        None
                    }
                };
                match warm_up {
                    Some(at) if at > Utc::now() => self.timers.set(code, at),
                    _ => self.poll(code),
                }
            }
            Done::Polled { code, polled } => {
                match polled {
                    Ok(Polled::Fresh(matches)) => self.announce(&code, matches),
                    Ok(Polled::Backlog(count)) => {
                        tracing::info!(event = %code, count, "Marked existing results as posted");
                    }
                    Ok(Polled::Unchanged) => {}
                    Err(err) => tracing::warn!(event = %code, error = %err, "Could not poll event"),
                }
                if let Some(tracked) = self.tracked.get(&code) {
                    let now = Utc::now();
                    let live = tracked.last_result.is_some_and(|t| now - t < LIVE_WINDOW);
                    self.timers
                        .set(code, now + if live { LIVE_INTERVAL } else { IDLE_INTERVAL });
                }
            }
            Done::Posted { gone } => {
                for channel in gone {
                    self.drop_channel(channel);
                }
                self.reconcile();
            }
            Done::Saved { what, saved } => {
                if let Err(err) = saved {
                    tracing::warn!(error = %err, "Could not save {what}");
                }
            }
        }
    }

    /// Tracks exactly the events something routes to, expiring those that are over.
    fn reconcile(&mut self) {
        let now = Utc::now();
        self.team_events
            .retain(|team, _| self.routes.teams.contains(team));
        let wanted: HashSet<EventCode> = self
            .routes
            .events
            .keys()
            .chain(self.team_events.values().flatten())
            .cloned()
            .collect();
        self.windows.retain(|code, _| wanted.contains(code));

        let open: HashSet<&EventCode> = self
            .windows
            .iter()
            .filter(|(_, w)| !w.is_over(now))
            .map(|(code, _)| code)
            .collect();
        let over: Vec<EventCode> = wanted
            .iter()
            .filter(|code| self.windows.contains_key(*code) && !open.contains(code))
            .cloned()
            .collect();

        self.tracked.retain(|code, _| {
            let keep = open.contains(code);
            if !keep {
                self.timers.cancel(code);
            }
            keep
        });
        for &code in &open {
            if !self.tracked.contains_key(code) {
                self.tracked.insert(code.clone(), Tracked::default());
                self.timers.set(code.clone(), now);
            }
        }
        for code in over {
            self.expire(code);
        }
    }

    fn expire(&mut self, code: EventCode) {
        if !self.routes.events.remove(&code) {
            return;
        }
        tracing::info!(event = %code, "Event over; dropping its subscriptions");
        let subscriptions = self.subscriptions.clone();
        self.tasks.spawn(async move {
            let saved = subscriptions.remove_event(&code).await;
            Done::Saved {
                what: "expired subscriptions",
                saved,
            }
        });
    }

    fn wake(&mut self, code: EventCode) {
        let (Some(window), Some(tracked)) = (self.windows.get(&code), self.tracked.get_mut(&code))
        else {
            return;
        };
        match window.phase(Utc::now()) {
            Phase::Upcoming(at) => self.timers.set(code, at),
            Phase::Over => self.reconcile(),
            Phase::Open { day } if tracked.warmed != Some(day) => {
                tracked.warmed = Some(day);
                let shared = self.shared.clone();
                self.tasks.spawn(async move {
                    let starts = shared.schedule(&code).await;
                    Done::Schedule { code, day, starts }
                });
            }
            Phase::Open { .. } => self.poll(code),
        }
    }

    fn poll(&mut self, code: EventCode) {
        let Some(tracked) = self.tracked.get(&code) else {
            return;
        };
        let Ok(mut feed) = tracked.feed.clone().try_lock_owned() else {
            return;
        };
        let shared = self.shared.clone();
        self.tasks.spawn(async move {
            let polled = feed.poll(&shared, &code).await;
            Done::Polled { code, polled }
        });
    }

    /// Re-wakes events left without a timer by a failed task.
    fn rearm(&mut self) {
        let now = Utc::now();
        for (code, tracked) in &self.tracked {
            if !self.timers.contains(code) && tracked.feed.try_lock().is_ok() {
                self.timers.set(code.clone(), now);
            }
        }
    }

    fn lookup_team(&mut self, team: u32) {
        let shared = self.shared.clone();
        self.tasks.spawn(async move {
            let events = shared.events("teamNumber", team.to_string()).await;
            Done::TeamEvents { team, events }
        });
    }

    fn lookup_event(&mut self, code: EventCode) {
        let shared = self.shared.clone();
        self.tasks.spawn(async move {
            let event = shared
                .events("eventCode", code.to_string())
                .await
                .map(|events| events.into_iter().next());
            Done::Event { code, event }
        });
    }

    /// Posts in result order, one card render per match.
    fn announce(&mut self, code: &EventCode, matches: Vec<Fresh>) {
        if let Some(tracked) = self.tracked.get_mut(code) {
            tracked.last_result = Some(Utc::now());
        }
        let posts: Vec<(BTreeSet<ChannelId>, Fresh)> = matches
            .into_iter()
            .map(|m| {
                let (red, blue) = alliance_teams(&m.info.teams);
                (self.routes.channels(code, red.into_iter().chain(blue)), m)
            })
            .filter(|(channels, _)| !channels.is_empty())
            .collect();
        if posts.is_empty() {
            return;
        }

        let name = self
            .windows
            .get(code)
            .map_or_else(|| code.to_string(), |w| w.name.clone());
        let (shared, code) = (self.shared.clone(), code.clone());
        self.tasks.spawn(async move {
            let mut gone = BTreeSet::new();
            for (channels, m) in posts {
                match Card::render(&shared, &m.info, m.rescored, &name, &code).await {
                    Ok(card) => gone.extend(card.post(&shared.http, &channels).await),
                    Err(err) => {
                        tracing::error!(event = %code, error = %err, "Could not render match card")
                    }
                }
            }
            Done::Posted { gone }
        });
    }

    fn drop_channel(&mut self, channel: ChannelId) {
        tracing::info!(%channel, "Channel no longer accepts posts; dropping its routes");
        self.routes.events.drop_channel(channel);
        let teams = self.routes.teams.drop_channel(channel);
        let (subscriptions, favorites) = (self.subscriptions.clone(), self.favorites.clone());
        self.tasks.spawn(async move {
            let saved = async {
                subscriptions.remove_channel(channel).await?;
                for (team, guild) in teams {
                    favorites.detach_channel(guild, team).await?;
                }
                Ok(())
            }
            .await;
            Done::Saved {
                what: "dropped channel",
                saved,
            }
        });
    }
}
