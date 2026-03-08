use serenity::model::id::GuildId;
use std::collections::{HashMap, HashSet};
use std::sync::{Arc, RwLock};

#[derive(Clone)]
pub struct FavoritesManager {
    favorites: Arc<RwLock<HashMap<GuildId, HashSet<i32>>>>,
}

impl FavoritesManager {
    pub fn new() -> Self {
        Self {
            favorites: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn add_favorite(&self, guild_id: GuildId, team_number: i32) -> bool {
        let mut favorites = self.favorites.write().unwrap();
        let guild_favorites = favorites.entry(guild_id).or_insert_with(HashSet::new);
        guild_favorites.insert(team_number)
    }

    pub fn remove_favorite(&self, guild_id: GuildId, team_number: i32) -> bool {
        let mut favorites = self.favorites.write().unwrap();
        if let Some(guild_favorites) = favorites.get_mut(&guild_id) {
            guild_favorites.remove(&team_number)
        } else {
            false
        }
    }

    pub fn is_favorite(&self, guild_id: GuildId, team_number: i32) -> bool {
        let favorites = self.favorites.read().unwrap();
        favorites
            .get(&guild_id)
            .map(|set| set.contains(&team_number))
            .unwrap_or(false)
    }

    pub fn toggle_favorite(&self, guild_id: GuildId, team_number: i32) -> bool {
        if self.is_favorite(guild_id, team_number) {
            self.remove_favorite(guild_id, team_number);
            false
        } else {
            self.add_favorite(guild_id, team_number);
            true
        }
    }

    pub fn list_favorites(&self, guild_id: GuildId) -> Vec<i32> {
        let favorites = self.favorites.read().unwrap();
        favorites
            .get(&guild_id)
            .map(|set| {
                let mut vec: Vec<i32> = set.iter().copied().collect();
                vec.sort();
                vec
            })
            .unwrap_or_default()
    }
}

impl Default for FavoritesManager {
    fn default() -> Self {
        Self::new()
    }
}
