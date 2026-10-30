use anyhow::{Context, Result};
use chrono::{Datelike, Utc};
use model::prelude::current_season;
use serenity::all::{ChannelId, GuildId};
use std::env;

use crate::store::parse_id;

#[derive(Clone, Debug)]
pub struct Config {
    pub discord_token: String,
    pub supabase_url: String,
    pub supabase_key: String,
    pub dev_server_id: Option<GuildId>,
    pub dev_channel_ids: Vec<ChannelId>,
    pub debug_mode: bool,
    /// `None` derives the season from the clock.
    pub season: Option<i32>,
    /// `None` disables live match cards.
    pub first_credentials: Option<(String, String)>,
}

impl Config {
    pub fn from_env() -> Result<Self> {
        dotenvy::dotenv().ok();

        let discord_token = env::var("DISCORD_TOKEN").context("DISCORD_TOKEN must be set")?;

        let supabase_url = env::var("SUPABASE_URL").context("SUPABASE_URL must be set")?;

        let supabase_key = env::var("SUPABASE_KEY").context("SUPABASE_KEY must be set")?;

        let dev_server_id = env::var("DEV_SERVER_ID1").ok().and_then(|s| parse_id(&s));

        let dev_channel_ids = ["DEV_CHANNEL_ID1", "DEV_CHANNEL_ID2"]
            .iter()
            .filter_map(|key| parse_id(&env::var(key).ok()?))
            .collect();

        let season = env::var("SEASON").ok().and_then(|s| s.parse().ok());

        let debug_mode = env::var("DEBUG_MODE")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(false);

        let first_credentials = env::var("FIRST_USERNAME")
            .ok()
            .zip(env::var("FIRST_PASS").ok());

        Ok(Config {
            discord_token,
            supabase_url,
            supabase_key,
            dev_server_id,
            dev_channel_ids,
            debug_mode,
            season,
            first_credentials,
        })
    }

    pub fn year(&self) -> i32 {
        self.season.unwrap_or_else(|| {
            let now = Utc::now();
            current_season(now.year(), now.month())
        })
    }
}
