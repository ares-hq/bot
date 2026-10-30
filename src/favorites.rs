use anyhow::Result;
use model::prelude::Supabase;
use model::tables;
use serde::{Deserialize, Serialize};
use serenity::model::id::{ChannelId, GuildId};
use std::collections::HashMap;
use std::sync::RwLock;

use crate::store::{Placement, parse_id};

#[derive(Serialize, Deserialize)]
struct FavoriteRow {
    guild_id: String,
    team_number: u32,
    #[serde(default)]
    channel_id: Option<String>,
}

/// `None` channel: starred, but match cards are not posted.
type GuildFavorites = HashMap<u32, Option<ChannelId>>;

pub struct FavoritesManager {
    client: Supabase,
    /// A present key means that guild is loaded.
    cache: RwLock<HashMap<GuildId, GuildFavorites>>,
}

impl FavoritesManager {
    pub fn new(client: Supabase) -> Self {
        Self {
            client,
            cache: RwLock::new(HashMap::new()),
        }
    }

    async fn ensure_loaded(&self, guild_id: GuildId) -> Result<()> {
        if self.cache.read().unwrap().contains_key(&guild_id) {
            return Ok(());
        }

        let rows: Vec<FavoriteRow> = self
            .client
            .select(tables::FAVORITES, &[("guild_id", format!("eq.{guild_id}"))])
            .await?;
        let loaded: GuildFavorites = rows
            .into_iter()
            .map(|r| (r.team_number, r.channel_id.as_deref().and_then(parse_id)))
            .collect();

        self.cache
            .write()
            .unwrap()
            .entry(guild_id)
            .or_insert(loaded);
        Ok(())
    }

    fn current(&self, guild_id: GuildId, team_number: u32) -> Option<Option<ChannelId>> {
        self.cache
            .read()
            .unwrap()
            .get(&guild_id)
            .and_then(|teams| teams.get(&team_number).copied())
    }

    pub async fn is_favorite(&self, guild_id: GuildId, team_number: u32) -> bool {
        if let Err(err) = self.ensure_loaded(guild_id).await {
            tracing::warn!(%guild_id, error = %err, "Could not read favorites");
            return false;
        }
        self.current(guild_id, team_number).is_some()
    }

    pub async fn list_favorites(&self, guild_id: GuildId) -> Result<Vec<(u32, Option<ChannelId>)>> {
        self.ensure_loaded(guild_id).await?;
        let cache = self.cache.read().unwrap();
        let mut teams: Vec<_> = cache
            .get(&guild_id)
            .map(|teams| teams.iter().map(|(&n, &c)| (n, c)).collect())
            .unwrap_or_default();
        teams.sort_unstable_by_key(|&(n, _)| n);
        Ok(teams)
    }

    pub async fn favorite(
        &self,
        guild_id: GuildId,
        team_number: u32,
        channel_id: ChannelId,
    ) -> Result<Placement> {
        self.ensure_loaded(guild_id).await?;
        let placement = Placement::decide(self.current(guild_id, team_number), channel_id);
        if placement != Placement::Unchanged {
            self.write(guild_id, team_number, Some(channel_id)).await?;
        }
        Ok(placement)
    }

    /// `false` when the team was not a favorite.
    pub async fn unfavorite(&self, guild_id: GuildId, team_number: u32) -> Result<bool> {
        self.ensure_loaded(guild_id).await?;
        if self.current(guild_id, team_number).is_none() {
            return Ok(false);
        }
        self.client
            .delete(
                tables::FAVORITES,
                &[
                    ("guild_id", format!("eq.{guild_id}")),
                    ("team_number", format!("eq.{team_number}")),
                ],
            )
            .await?;
        if let Some(teams) = self.cache.write().unwrap().get_mut(&guild_id) {
            teams.remove(&team_number);
        }
        Ok(true)
    }

    /// Keeps the star but stops posting cards, e.g. when the channel is gone.
    pub async fn detach_channel(&self, guild_id: GuildId, team_number: u32) -> Result<()> {
        self.write(guild_id, team_number, None).await
    }

    async fn write(
        &self,
        guild_id: GuildId,
        team_number: u32,
        channel_id: Option<ChannelId>,
    ) -> Result<()> {
        let row = FavoriteRow {
            guild_id: guild_id.to_string(),
            team_number,
            channel_id: channel_id.map(|c| c.to_string()),
        };
        self.client
            .upsert(tables::FAVORITES, &[row], Some("guild_id,team_number"))
            .await?;
        if let Some(teams) = self.cache.write().unwrap().get_mut(&guild_id) {
            teams.insert(team_number, channel_id);
        }
        Ok(())
    }

    /// Every favorite in every guild that has a channel to post to.
    pub async fn announced(&self) -> Result<Vec<(GuildId, u32, ChannelId)>> {
        let rows: Vec<FavoriteRow> = self
            .client
            .select(tables::FAVORITES, &[("channel_id", "not.is.null".into())])
            .await?;
        Ok(rows
            .into_iter()
            .filter_map(|r| {
                let channel = parse_id(r.channel_id.as_deref()?)?;
                Some((parse_id(&r.guild_id)?, r.team_number, channel))
            })
            .collect())
    }
}
