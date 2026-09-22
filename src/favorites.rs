//! ```sql
//! create table favorites (
//!   guild_id    text    not null,
//!   team_number integer not null,
//!   primary key (guild_id, team_number)
//! );
//! ```

use anyhow::Result;
use model::prelude::Supabase;
use model::tables;
use serde::{Deserialize, Serialize};
use serenity::model::id::GuildId;
use std::collections::{HashMap, HashSet};
use std::sync::RwLock;

#[derive(Serialize, Deserialize)]
struct FavoriteRow {
    guild_id: String,
    team_number: u32,
}

pub struct FavoritesManager {
    client: Supabase,
    /// A present key means that guild is loaded.
    cache: RwLock<HashMap<GuildId, HashSet<u32>>>,
}

impl FavoritesManager {
    pub fn new(supabase_url: &str, supabase_key: String) -> Self {
        Self {
            client: Supabase::new(supabase_url, supabase_key),
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
        let loaded: HashSet<u32> = rows.into_iter().map(|r| r.team_number).collect();

        self.cache
            .write()
            .unwrap()
            .entry(guild_id)
            .or_insert(loaded);
        Ok(())
    }

    fn contains(&self, guild_id: GuildId, team_number: u32) -> bool {
        self.cache
            .read()
            .unwrap()
            .get(&guild_id)
            .is_some_and(|set| set.contains(&team_number))
    }

    pub async fn is_favorite(&self, guild_id: GuildId, team_number: u32) -> bool {
        if let Err(err) = self.ensure_loaded(guild_id).await {
            tracing::warn!(%guild_id, error = %err, "Could not read favorites");
            return false;
        }
        self.contains(guild_id, team_number)
    }

    pub async fn list_favorites(&self, guild_id: GuildId) -> Result<Vec<u32>> {
        self.ensure_loaded(guild_id).await?;
        let cache = self.cache.read().unwrap();
        let mut teams: Vec<u32> = cache
            .get(&guild_id)
            .map(|set| set.iter().copied().collect())
            .unwrap_or_default();
        teams.sort_unstable();
        Ok(teams)
    }

    /// `true` if added, `false` if removed.
    pub async fn toggle_favorite(&self, guild_id: GuildId, team_number: u32) -> Result<bool> {
        self.ensure_loaded(guild_id).await?;
        let adding = !self.contains(guild_id, team_number);

        if adding {
            let row = FavoriteRow {
                guild_id: guild_id.to_string(),
                team_number,
            };
            self.client
                .upsert(tables::FAVORITES, &[row], Some("guild_id,team_number"))
                .await?;
        } else {
            self.client
                .delete(
                    tables::FAVORITES,
                    &[
                        ("guild_id", format!("eq.{guild_id}")),
                        ("team_number", format!("eq.{team_number}")),
                    ],
                )
                .await?;
        }

        let mut cache = self.cache.write().unwrap();
        let set = cache.entry(guild_id).or_default();
        if adding {
            set.insert(team_number);
        } else {
            set.remove(&team_number);
        }
        Ok(adding)
    }
}
