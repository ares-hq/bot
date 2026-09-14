use anyhow::{Context, Result};
use chrono::{Datelike, Utc};
use model::prelude::{Supabase, Team, current_season};

/// Reads team rows from the season table, always fetching the latest (no cache).
pub struct Teams {
    client: Supabase,
    table: String,
}

impl Teams {
    pub fn new(supabase_url: String, supabase_key: String) -> Self {
        let now = Utc::now();
        let year = current_season(now.year(), now.month());
        Self {
            client: Supabase::new(&supabase_url, supabase_key),
            table: format!("season_{year}"),
        }
    }

    pub async fn get_team(&self, team_number: u32) -> Result<Team> {
        self.client
            .team(&self.table, team_number)
            .await
            .context("failed to read team")?
            .context("team not found")
    }
}
