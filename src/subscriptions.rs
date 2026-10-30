use anyhow::Result;
use model::first::EventCode;
use model::prelude::Supabase;
use model::supabase::Filter;
use model::tables;
use serde::{Deserialize, Serialize};
use serenity::model::id::{ChannelId, GuildId};

use crate::store::{Placement, parse_id};

#[derive(Serialize, Deserialize)]
struct SubscriptionRow {
    guild_id: String,
    season: i32,
    event_code: EventCode,
    channel_id: String,
}

impl SubscriptionRow {
    fn parse(self) -> Option<(GuildId, EventCode, ChannelId)> {
        Some((
            parse_id(&self.guild_id)?,
            self.event_code,
            parse_id(&self.channel_id)?,
        ))
    }
}

pub struct Subscriptions {
    client: Supabase,
    season: i32,
}

impl Subscriptions {
    pub fn new(client: Supabase, season: i32) -> Self {
        Self { client, season }
    }

    fn season_filter(&self) -> Filter<'static> {
        ("season", format!("eq.{}", self.season))
    }

    async fn rows(&self, filters: &[Filter<'_>]) -> Result<Vec<(GuildId, EventCode, ChannelId)>> {
        let mut query = vec![self.season_filter()];
        query.extend(filters.iter().cloned());
        let rows: Vec<SubscriptionRow> = self
            .client
            .select_all(tables::EVENT_SUBSCRIPTIONS, &query, "guild_id,event_code")
            .await?;
        Ok(rows
            .into_iter()
            .filter_map(SubscriptionRow::parse)
            .collect())
    }

    /// Sorted by event.
    pub async fn list(&self, guild_id: GuildId) -> Result<Vec<(EventCode, ChannelId)>> {
        let mut subs: Vec<_> = self
            .rows(&[("guild_id", format!("eq.{guild_id}"))])
            .await?
            .into_iter()
            .map(|(_, code, channel)| (code, channel))
            .collect();
        subs.sort();
        Ok(subs)
    }

    pub async fn all(&self) -> Result<Vec<(GuildId, EventCode, ChannelId)>> {
        self.rows(&[]).await
    }

    fn key(guild_id: GuildId, code: &EventCode) -> [Filter<'static>; 2] {
        [
            ("guild_id", format!("eq.{guild_id}")),
            ("event_code", format!("eq.{code}")),
        ]
    }

    async fn current(&self, guild_id: GuildId, code: &EventCode) -> Result<Option<ChannelId>> {
        let rows = self.rows(&Self::key(guild_id, code)).await?;
        Ok(rows.first().map(|&(_, _, channel)| channel))
    }

    pub async fn subscribe(
        &self,
        guild_id: GuildId,
        code: &EventCode,
        channel_id: ChannelId,
    ) -> Result<Placement> {
        let current = self.current(guild_id, code).await?.map(Some);
        let placement = Placement::decide(current, channel_id);
        if placement != Placement::Unchanged {
            let row = SubscriptionRow {
                guild_id: guild_id.to_string(),
                season: self.season,
                event_code: code.clone(),
                channel_id: channel_id.to_string(),
            };
            self.client
                .upsert(tables::EVENT_SUBSCRIPTIONS, &[row], None)
                .await?;
        }
        Ok(placement)
    }

    /// `false` when the guild was not subscribed.
    pub async fn unsubscribe(&self, guild_id: GuildId, code: &EventCode) -> Result<bool> {
        if self.current(guild_id, code).await?.is_none() {
            return Ok(false);
        }
        let [guild, event] = Self::key(guild_id, code);
        self.client
            .delete(
                tables::EVENT_SUBSCRIPTIONS,
                &[guild, self.season_filter(), event],
            )
            .await?;
        Ok(true)
    }

    pub async fn remove_channel(&self, channel_id: ChannelId) -> Result<()> {
        self.client
            .delete(
                tables::EVENT_SUBSCRIPTIONS,
                &[("channel_id", format!("eq.{channel_id}"))],
            )
            .await
    }

    pub async fn remove_event(&self, code: &EventCode) -> Result<()> {
        self.client
            .delete(
                tables::EVENT_SUBSCRIPTIONS,
                &[self.season_filter(), ("event_code", format!("eq.{code}"))],
            )
            .await
    }
}
