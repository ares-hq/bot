use anyhow::Result;
use model::first::{EventCode, MatchInfo, MatchesResponse};
use model::tables;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use super::Shared;

#[derive(Serialize, Deserialize)]
struct PostedRow {
    season: i32,
    event_code: EventCode,
    matchcode: String,
    /// `None` on rows that predate score tracking.
    #[serde(default)]
    score: Option<String>,
}

pub struct Fresh {
    pub info: MatchInfo,
    /// Posted before with a different score.
    pub rescored: bool,
}

pub enum Polled {
    Unchanged,
    /// Results that predate the first watch; recorded, never posted.
    Backlog(usize),
    Fresh(Vec<Fresh>),
}

/// Per-event fetch state; `posted` loads lazily from `posted_matches`.
#[derive(Default)]
pub struct Feed {
    posted: Option<HashMap<String, Option<String>>>,
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
                .map(|f| PostedRow {
                    season: shared.season,
                    event_code: code.clone(),
                    matchcode: f.info.key(),
                    score: Some(scoreline(&f.info)),
                })
                .collect();
            shared
                .db
                .upsert(
                    tables::POSTED_MATCHES,
                    &rows,
                    Some("season,event_code,matchcode"),
                )
                .await?;
            posted.extend(rows.into_iter().map(|r| (r.matchcode, r.score)));
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

/// Every figure a result card shows.
fn scoreline(m: &MatchInfo) -> String {
    format!(
        "{}/{}/{}-{}/{}/{}",
        m.score_red_final,
        m.score_red_auto,
        m.score_red_foul,
        m.score_blue_final,
        m.score_blue_auto,
        m.score_blue_foul
    )
}

/// Scored results not yet posted, or posted with another score, in commit order.
fn unposted(posted: &HashMap<String, Option<String>>, matches: Vec<MatchInfo>) -> Vec<Fresh> {
    let mut fresh: Vec<Fresh> = matches
        .into_iter()
        .filter(MatchInfo::is_scored)
        .filter_map(|info| {
            let rescored = match posted.get(&info.key()) {
                None => false,
                Some(Some(score)) if *score != scoreline(&info) => true,
                Some(_) => return None,
            };
            Some(Fresh { info, rescored })
        })
        .collect();
    fresh.sort_by(|a, b| a.info.post_result_time.cmp(&b.info.post_result_time));
    fresh
}

async fn load_posted(shared: &Shared, code: &EventCode) -> Result<HashMap<String, Option<String>>> {
    let rows: Vec<PostedRow> = shared
        .db
        .select_all(
            tables::POSTED_MATCHES,
            &[
                ("season", format!("eq.{}", shared.season)),
                ("event_code", format!("eq.{code}")),
            ],
            "matchcode",
        )
        .await?;
    Ok(rows.into_iter().map(|r| (r.matchcode, r.score)).collect())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn result(number: i64, posted_at: Option<&str>, red: i64) -> MatchInfo {
        serde_json::from_value(json!({
            "tournamentLevel": "QUALIFICATION", "matchNumber": number,
            "postResultTime": posted_at, "scoreRedFinal": red,
        }))
        .unwrap()
    }

    fn numbers(fresh: &[Fresh]) -> Vec<(i64, bool)> {
        fresh
            .iter()
            .map(|f| (f.info.match_number, f.rescored))
            .collect()
    }

    #[test]
    fn only_new_scored_results_come_through_in_commit_order() {
        let first = result(1, Some("2026-10-29T18:00:00"), 10);
        let posted = HashMap::from([(first.key(), Some(scoreline(&first)))]);
        let matches = vec![
            first,
            result(3, Some("2026-10-29T18:20:00"), 10),
            result(2, Some("2026-10-29T18:10:00"), 10),
            result(4, None, 0),
        ];
        assert_eq!(
            numbers(&unposted(&posted, matches)),
            [(2, false), (3, false)]
        );
    }

    #[test]
    fn a_rescored_result_comes_through_again() {
        let before = result(1, Some("2026-10-29T18:00:00"), 10);
        let posted = HashMap::from([(before.key(), Some(scoreline(&before)))]);
        let after = result(1, Some("2026-10-29T18:05:00"), 12);
        assert_eq!(numbers(&unposted(&posted, vec![after])), [(1, true)]);
    }

    #[test]
    fn a_result_posted_before_scores_were_kept_is_not_reposted() {
        let m = result(1, Some("2026-10-29T18:00:00"), 10);
        let posted = HashMap::from([(m.key(), None)]);
        assert!(unposted(&posted, vec![m]).is_empty());
    }
}
