use anyhow::{Context, Result};
use chrono::{Datelike, Utc};
use postgrest::Postgrest;
use serde::{Deserialize, Deserializer};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TeamData {
    #[serde(default, deserialize_with = "deserialize_i32_default")]
    pub team_number: i32,
    #[serde(default, deserialize_with = "deserialize_string_default")]
    pub team_name: String,
    pub sponsors: Option<String>,
    pub location: Option<String>,
    #[serde(default, deserialize_with = "deserialize_f64_default")]
    pub auto_opr: f64,
    #[serde(default, deserialize_with = "deserialize_f64_default")]
    pub tele_opr: f64,
    #[serde(default, deserialize_with = "deserialize_f64_default")]
    pub endgame_opr: f64,
    #[serde(default, deserialize_with = "deserialize_f64_default")]
    pub overall_opr: f64,
    #[serde(default, deserialize_with = "deserialize_f64_default")]
    pub penalties: f64,
    pub auto_rank: Option<i32>,
    pub tele_rank: Option<i32>,
    pub endgame_rank: Option<i32>,
    pub overall_rank: Option<i32>,
    pub penalty_rank: Option<i32>,
    pub profile_update: Option<String>,
    pub event_date: Option<String>,
}

fn deserialize_i32_default<'de, D>(deserializer: D) -> std::result::Result<i32, D::Error>
where
    D: Deserializer<'de>,
{
    let value: Option<serde_json::Value> = Option::deserialize(deserializer)?;
    let parsed = value
        .as_ref()
        .and_then(|v| v.as_i64().or_else(|| v.as_str().and_then(|s| s.parse::<i64>().ok())))
        .unwrap_or(0);

    Ok(parsed as i32)
}

fn deserialize_f64_default<'de, D>(deserializer: D) -> std::result::Result<f64, D::Error>
where
    D: Deserializer<'de>,
{
    let value: Option<serde_json::Value> = Option::deserialize(deserializer)?;
    Ok(value
        .as_ref()
        .and_then(|v| v.as_f64().or_else(|| v.as_str().and_then(|s| s.parse::<f64>().ok())))
        .unwrap_or(0.0))
}

fn deserialize_string_default<'de, D>(deserializer: D) -> std::result::Result<String, D::Error>
where
    D: Deserializer<'de>,
{
    let value: Option<serde_json::Value> = Option::deserialize(deserializer)?;
    Ok(value
        .as_ref()
        .and_then(|v| v.as_str().map(ToOwned::to_owned))
        .unwrap_or_else(|| "Unknown".to_owned()))
}

pub struct SupabaseHandler {
    supabase_url: String,
    supabase_key: String,
    cache: Arc<RwLock<HashMap<i32, TeamData>>>,
    table_name: String,
}

impl SupabaseHandler {
    pub fn new(supabase_url: String, supabase_key: String) -> Self {
        let year = Self::find_year();
        let table_name = format!("season_{}", year);

        Self {
            supabase_url,
            supabase_key,
            cache: Arc::new(RwLock::new(HashMap::new())),
            table_name,
        }
    }

    pub fn find_year() -> i32 {
        let now = Utc::now();
        let year = now.year();
        let month = now.month();

        if month < 8 { year - 1 } else { year }
    }

    pub async fn get_team(&self, team_number: i32) -> Result<TeamData> {
        {
            let cache = self.cache.read().unwrap();
            if let Some(team) = cache.get(&team_number) {
                return Ok(team.clone());
            }
        }

        // Create postgrest client with Supabase authentication
        let client = Postgrest::new(format!("{}/rest/v1", self.supabase_url))
            .insert_header("apikey", &self.supabase_key)
            .insert_header("Authorization", format!("Bearer {}", self.supabase_key));

        let response = client
            .from(&self.table_name)
            .select("*")
            .eq("teamNumber", &team_number.to_string())
            .limit(1)
            .execute()
            .await
            .context("Failed to query Supabase")?;

        let body = response
            .text()
            .await
            .context("Failed to read response body")?;
        let mut teams: Vec<TeamData> =
            serde_json::from_str(&body).with_context(|| {
                let snippet: String = body.chars().take(300).collect();
                format!("Failed to parse team data. Response starts with: {}", snippet)
            })?;

        let team = teams.pop().context("Team not found")?;

        {
            let mut cache = self.cache.write().unwrap();
            cache.insert(team_number, team.clone());
        }

        Ok(team)
    }
}
