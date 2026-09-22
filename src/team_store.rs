use anyhow::{Context, Result};
use chrono::{Datelike, Utc};
use model::prelude::{Supabase, Team, current_season};
use model::tables;
use std::collections::HashMap;
use std::sync::RwLock;
use std::time::{Duration, Instant};

const TTL: Duration = Duration::from_secs(60);

struct Cached {
    team: Team,
    fetched: Instant,
}

pub struct TeamStore {
    client: Supabase,
    table: String,
    cache: RwLock<HashMap<u32, Cached>>,
    ttl: Duration,
}

impl TeamStore {
    pub fn new(supabase_url: &str, supabase_key: String, season: Option<i32>) -> Self {
        let year = season.unwrap_or_else(|| {
            let now = Utc::now();
            current_season(now.year(), now.month())
        });
        Self {
            client: Supabase::new(supabase_url, supabase_key),
            table: tables::season(year),
            cache: RwLock::new(HashMap::new()),
            ttl: TTL,
        }
    }

    fn cached(&self, number: u32) -> Option<Team> {
        let cache = self.cache.read().unwrap();
        let entry = cache.get(&number)?;
        (entry.fetched.elapsed() < self.ttl).then(|| entry.team.clone())
    }

    fn store(&self, teams: &[Team]) {
        let fetched = Instant::now();
        let mut cache = self.cache.write().unwrap();
        for team in teams {
            cache.insert(
                team.number,
                Cached {
                    team: team.clone(),
                    fetched,
                },
            );
        }
    }

    /// Unlisted teams are absent from the result, not an error.
    pub async fn teams(&self, numbers: &[u32]) -> Result<Vec<Team>> {
        let mut found = Vec::with_capacity(numbers.len());
        let mut missing = Vec::new();

        for &number in numbers {
            match self.cached(number) {
                Some(team) => found.push(team),
                None => missing.push(number),
            }
        }

        if !missing.is_empty() {
            let fetched = self
                .client
                .teams_in(&self.table, &missing)
                .await
                .context("failed to read teams")?;
            self.store(&fetched);
            found.extend(fetched);
        }

        Ok(found)
    }

    pub async fn team(&self, team_number: u32) -> Result<Team> {
        if let Some(team) = self.cached(team_number) {
            return Ok(team);
        }

        let team = self
            .client
            .team(&self.table, team_number)
            .await
            .context("failed to read team")?
            .context("team not found")?;
        self.store(std::slice::from_ref(&team));
        Ok(team)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn store(ttl: Duration) -> TeamStore {
        let mut store = TeamStore::new("https://example.invalid", "key".into(), Some(2025));
        store.ttl = ttl;
        store
    }

    fn team(number: u32) -> Team {
        Team::new(number, format!("Team {number}"))
    }

    #[test]
    fn the_season_pins_the_table() {
        assert_eq!(store(TTL).table, "season_2025");
    }

    #[test]
    fn a_stored_team_reads_back_without_a_request() {
        let store = store(TTL);
        store.store(&[team(254)]);
        assert_eq!(store.cached(254).map(|t| t.number), Some(254));
    }

    #[test]
    fn an_unknown_team_is_not_cached() {
        assert!(store(TTL).cached(254).is_none());
    }

    #[test]
    fn an_expired_entry_is_not_served() {
        let store = store(Duration::ZERO);
        store.store(&[team(254)]);
        assert!(store.cached(254).is_none(), "served a stale row");
    }
}
