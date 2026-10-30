use anyhow::Result;
use model::first::{EventCode, MatchInfo, MatchesResponse};
use model::tables;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

use super::Shared;

#[derive(Serialize, Deserialize)]
struct PostedRow {
    event_code: EventCode,
    matchcode: String,
}

pub enum Polled {
    Unchanged,
    /// Results that predate the first watch; recorded, never posted.
    Backlog(usize),
    Fresh(Vec<MatchInfo>),
}

/// Per-event fetch state; `posted` loads lazily from `posted_matches`.
#[derive(Default)]
pub struct Feed {
    posted: Option<HashSet<String>>,
    backlog: bool,
    last_modified: Option<String>,
}

impl Feed {
    pub async fn poll(&mut self, shared: &Shared, code: &EventCode) -> Result<Polled> {
        if self.posted.is_none() {
            let posted = load_posted(shared, code).await?;
            self.backlog = posted.is_empty();
            self.posted = Some(posted);
        }

        let params = shared.params(["matches", code.as_str()]);
        let Some((resp, modified)) = shared
            .first
            .get_if_modified::<MatchesResponse>(&params, self.last_modified.as_deref())
            .await?
        else {
            return Ok(Polled::Unchanged);
        };

        let posted = self.posted.get_or_insert_default();
        let fresh = unposted(posted, resp.matches);
        if !fresh.is_empty() {
            let rows: Vec<PostedRow> = fresh
                .iter()
                .map(|m| PostedRow {
                    event_code: code.clone(),
                    matchcode: m.key(),
                })
                .collect();
            shared
                .db
                .upsert(tables::POSTED_MATCHES, &rows, Some("event_code,matchcode"))
                .await?;
            posted.extend(rows.into_iter().map(|r| r.matchcode));
        }
        self.last_modified = modified;

        let backlog = std::mem::take(&mut self.backlog);
        Ok(if fresh.is_empty() {
            Polled::Unchanged
        } else if backlog {
            Polled::Backlog(fresh.len())
        } else {
            Polled::Fresh(fresh)
        })
    }
}

/// Scored and not yet posted, in the order results were committed.
fn unposted(posted: &HashSet<String>, matches: Vec<MatchInfo>) -> Vec<MatchInfo> {
    let mut fresh: Vec<_> = matches
        .into_iter()
        .filter(|m| m.is_scored() && !posted.contains(&m.key()))
        .collect();
    fresh.sort_by(|a, b| a.post_result_time.cmp(&b.post_result_time));
    fresh
}

async fn load_posted(shared: &Shared, code: &EventCode) -> Result<HashSet<String>> {
    let rows: Vec<PostedRow> = shared
        .db
        .select(
            tables::POSTED_MATCHES,
            &[
                ("event_code", format!("eq.{code}")),
                ("select", "event_code,matchcode".into()),
            ],
        )
        .await?;
    Ok(rows.into_iter().map(|r| r.matchcode).collect())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn result(number: i64, posted_at: Option<&str>) -> MatchInfo {
        serde_json::from_value(json!({
            "tournamentLevel": "QUALIFICATION", "matchNumber": number,
            "postResultTime": posted_at,
        }))
        .unwrap()
    }

    #[test]
    fn only_new_scored_results_come_through_in_commit_order() {
        let posted = HashSet::from([result(1, None).key()]);
        let matches = vec![
            result(1, Some("2026-10-29T18:00:00")),
            result(3, Some("2026-10-29T18:20:00")),
            result(2, Some("2026-10-29T18:10:00")),
            result(4, None),
        ];
        let numbers: Vec<_> = unposted(&posted, matches)
            .iter()
            .map(|m| m.match_number)
            .collect();
        assert_eq!(numbers, [2, 3]);
    }
}
