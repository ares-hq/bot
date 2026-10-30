use model::first::EventCode;
use serenity::all::{ChannelId, GuildId};
use std::collections::{BTreeSet, HashMap};
use std::hash::Hash;

/// Each guild posts a key to at most one channel.
pub struct Table<K>(HashMap<K, HashMap<GuildId, ChannelId>>);

impl<K> Default for Table<K> {
    fn default() -> Self {
        Self(HashMap::new())
    }
}

impl<K: Eq + Hash + Clone> Table<K> {
    pub fn follow(&mut self, key: K, guild: GuildId, channel: ChannelId) {
        self.0.entry(key).or_default().insert(guild, channel);
    }

    pub fn unfollow(&mut self, key: &K, guild: GuildId) {
        if let Some(guilds) = self.0.get_mut(key) {
            guilds.remove(&guild);
            if guilds.is_empty() {
                self.0.remove(key);
            }
        }
    }

    pub fn remove(&mut self, key: &K) -> bool {
        self.0.remove(key).is_some()
    }

    pub fn contains(&self, key: &K) -> bool {
        self.0.contains_key(key)
    }

    pub fn keys(&self) -> impl Iterator<Item = &K> {
        self.0.keys()
    }

    fn channels(&self, key: &K) -> impl Iterator<Item = ChannelId> + '_ {
        self.0
            .get(key)
            .into_iter()
            .flat_map(|g| g.values().copied())
    }

    /// Returns what pointed at `channel`.
    pub fn drop_channel(&mut self, channel: ChannelId) -> Vec<(K, GuildId)> {
        let mut dropped = Vec::new();
        self.0.retain(|key, guilds| {
            guilds.retain(|&guild, &mut c| {
                let gone = c == channel;
                if gone {
                    dropped.push((key.clone(), guild));
                }
                !gone
            });
            !guilds.is_empty()
        });
        dropped
    }
}

#[derive(Default)]
pub struct Routes {
    pub events: Table<EventCode>,
    pub teams: Table<u32>,
}

impl Routes {
    pub fn channels(
        &self,
        event: &EventCode,
        teams: impl IntoIterator<Item = u32>,
    ) -> BTreeSet<ChannelId> {
        let mut channels: BTreeSet<_> = self.events.channels(event).collect();
        for team in teams {
            channels.extend(self.teams.channels(&team));
        }
        channels
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const GUILD: GuildId = GuildId::new(1);
    const OTHER_GUILD: GuildId = GuildId::new(2);
    const HERE: ChannelId = ChannelId::new(10);
    const THERE: ChannelId = ChannelId::new(20);

    fn code(s: &str) -> EventCode {
        s.parse().unwrap()
    }

    #[test]
    fn an_event_and_a_team_in_one_channel_post_once() {
        let mut r = Routes::default();
        r.events.follow(code("USAZTUQ"), GUILD, HERE);
        r.teams.follow(14584, GUILD, HERE);
        r.teams.follow(1678, OTHER_GUILD, THERE);
        assert_eq!(
            r.channels(&code("USAZTUQ"), [14584, 1678]),
            BTreeSet::from([HERE, THERE])
        );
        assert!(r.channels(&code("B"), [9999]).is_empty());
    }

    #[test]
    fn following_again_moves_the_guild() {
        let mut r = Routes::default();
        r.teams.follow(14584, GUILD, HERE);
        r.teams.follow(14584, GUILD, THERE);
        assert_eq!(
            r.channels(&code("USAZTUQ"), [14584]),
            BTreeSet::from([THERE])
        );
    }

    #[test]
    fn the_last_unfollow_forgets_the_key() {
        let mut r = Routes::default();
        r.events.follow(code("USAZTUQ"), GUILD, HERE);
        r.events.follow(code("USAZTUQ"), OTHER_GUILD, THERE);
        r.events.unfollow(&code("USAZTUQ"), GUILD);
        assert!(r.events.contains(&code("USAZTUQ")));
        r.events.unfollow(&code("USAZTUQ"), OTHER_GUILD);
        assert!(!r.events.contains(&code("USAZTUQ")));
    }

    #[test]
    fn dropping_a_channel_reports_and_removes_its_routes() {
        let mut r = Routes::default();
        r.teams.follow(14584, GUILD, HERE);
        r.teams.follow(1678, GUILD, THERE);
        assert_eq!(r.teams.drop_channel(HERE), [(14584, GUILD)]);
        assert!(!r.teams.contains(&14584));
        assert!(r.teams.contains(&1678));
    }
}
