use anyhow::{Context, Result};
use std::env;

#[derive(Clone, Debug)]
pub struct Config {
    pub discord_token: String,
    pub supabase_url: String,
    pub supabase_key: String,
    pub dev_server_id: Option<u64>,
    pub dev_channel_ids: Vec<u64>,
    pub debug_mode: bool,
}

impl Config {
    pub fn from_env() -> Result<Self> {
        dotenvy::dotenv().ok();

        let discord_token = env::var("DISCORD_TOKEN").context("DISCORD_TOKEN must be set")?;

        let supabase_url = env::var("SUPABASE_URL").context("SUPABASE_URL must be set")?;

        let supabase_key = env::var("SUPABASE_KEY").context("SUPABASE_KEY must be set")?;

        let dev_server_id = env::var("DEV_SERVER_ID1").ok().and_then(|s| s.parse().ok());

        let mut dev_channel_ids = Vec::new();
        if let Ok(id_str) = env::var("DEV_CHANNEL_ID1") {
            if let Ok(id) = id_str.parse::<u64>() {
                dev_channel_ids.push(id);
            }
        }
        if let Ok(id_str) = env::var("DEV_CHANNEL_ID2") {
            if let Ok(id) = id_str.parse::<u64>() {
                dev_channel_ids.push(id);
            }
        }

        let debug_mode = env::var("DEBUG_MODE")
            .unwrap_or_else(|_| "false".to_string())
            .parse::<bool>()
            .unwrap_or(false);

        Ok(Config {
            discord_token,
            supabase_url,
            supabase_key,
            dev_server_id,
            dev_channel_ids,
            debug_mode,
        })
    }
}
