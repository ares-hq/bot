use chrono::offset::LocalResult;
use chrono::{DateTime, NaiveDate, NaiveDateTime, NaiveTime, TimeDelta, TimeZone, Utc};
use model::first::{EventSummary, Tz};

/// Venue-local; polling for a day runs from `OPEN` until `CLOSE` the next morning.
const OPEN: NaiveTime = NaiveTime::from_hms_opt(6, 0, 0).unwrap();
const CLOSE: NaiveTime = NaiveTime::from_hms_opt(2, 0, 0).unwrap();
const LEAD: TimeDelta = TimeDelta::minutes(30);
/// Unknown zone: the earliest opening and latest close anywhere on Earth.
const EARLIEST_ZONE: Tz = Tz::Pacific__Kiritimati;
const LATEST_ZONE: Tz = Tz::Etc__GMTPlus12;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Phase {
    Upcoming(DateTime<Utc>),
    Open { day: NaiveDate },
    Over,
}

#[derive(Debug, Clone)]
pub struct EventWindow {
    pub name: String,
    zone: Option<Tz>,
    first_day: NaiveDate,
    last_day: NaiveDate,
}

impl EventWindow {
    pub fn from_summary(event: &EventSummary) -> Option<Self> {
        let first_day = event.date_start?.date();
        let last_day = event
            .date_end
            .map_or(first_day, |end| end.date().max(first_day));
        Some(Self {
            name: event
                .name
                .clone()
                .or_else(|| event.code.as_ref().map(ToString::to_string))
                .unwrap_or_default(),
            zone: event.timezone,
            first_day,
            last_day,
        })
    }

    pub fn phase(&self, now: DateTime<Utc>) -> Phase {
        for day in self
            .first_day
            .iter_days()
            .take_while(|&d| d <= self.last_day)
        {
            if now < self.opens(day) {
                return Phase::Upcoming(self.opens(day));
            }
            if now < self.closes(day) {
                return Phase::Open { day };
            }
        }
        Phase::Over
    }

    pub fn is_over(&self, now: DateTime<Utc>) -> bool {
        self.phase(now) == Phase::Over
    }

    /// `LEAD` before the first match scheduled on `day`, if the schedule has one.
    pub fn warm_up(
        &self,
        day: NaiveDate,
        starts: impl IntoIterator<Item = NaiveDateTime>,
    ) -> Option<DateTime<Utc>> {
        let zone = self.zone?;
        let first = starts.into_iter().filter(|s| s.date() == day).min()?;
        Some(to_utc(zone, first) - LEAD)
    }

    fn opens(&self, day: NaiveDate) -> DateTime<Utc> {
        to_utc(self.zone.unwrap_or(EARLIEST_ZONE), day.and_time(OPEN))
    }

    fn closes(&self, day: NaiveDate) -> DateTime<Utc> {
        let next = day.succ_opt().unwrap_or(day);
        to_utc(self.zone.unwrap_or(LATEST_ZONE), next.and_time(CLOSE))
    }
}

/// A local time skipped by a DST jump resolves to just after the jump.
fn to_utc(zone: Tz, local: NaiveDateTime) -> DateTime<Utc> {
    match zone.from_local_datetime(&local) {
        LocalResult::Single(t) | LocalResult::Ambiguous(t, _) => t.with_timezone(&Utc),
        LocalResult::None => to_utc(zone, local + TimeDelta::hours(1)),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn window(start: &str, end: &str, zone: Option<&str>) -> EventWindow {
        let summary: EventSummary = serde_json::from_value(json!({
            "code": "USAZTUQ", "name": "Diamondback - Tucson Qualifier",
            "dateStart": format!("{start}T00:00:00"),
            "dateEnd": format!("{end}T00:00:00"),
            "timezone": zone,
        }))
        .unwrap();
        EventWindow::from_summary(&summary).unwrap()
    }

    fn utc(s: &str) -> DateTime<Utc> {
        s.parse().unwrap()
    }

    fn day(s: &str) -> NaiveDate {
        s.parse().unwrap()
    }

    #[test]
    fn opening_follows_the_venue_zone() {
        let phoenix = window("2026-02-20", "2026-02-20", Some("America/Phoenix"));
        let berlin = window("2026-02-20", "2026-02-20", Some("Europe/Berlin"));
        let now = utc("2026-01-01T00:00:00Z");
        assert_eq!(
            phoenix.phase(now),
            Phase::Upcoming(utc("2026-02-20T13:00:00Z"))
        );
        assert_eq!(
            berlin.phase(now),
            Phase::Upcoming(utc("2026-02-20T05:00:00Z"))
        );
    }

    #[test]
    fn a_multi_day_event_sleeps_between_days() {
        let w = window("2026-03-14", "2026-03-15", Some("America/Phoenix"));
        assert_eq!(
            w.phase(utc("2026-03-14T20:00:00Z")),
            Phase::Open {
                day: day("2026-03-14")
            }
        );
        assert_eq!(
            w.phase(utc("2026-03-15T10:00:00Z")),
            Phase::Upcoming(utc("2026-03-15T13:00:00Z"))
        );
        assert_eq!(
            w.phase(utc("2026-03-16T08:59:00Z")),
            Phase::Open {
                day: day("2026-03-15")
            }
        );
        assert!(w.is_over(utc("2026-03-16T09:00:00Z")));
    }

    #[test]
    fn a_close_inside_the_spring_forward_gap_lands_after_it() {
        let w = window("2026-03-07", "2026-03-07", Some("America/New_York"));
        assert!(!w.is_over(utc("2026-03-08T06:59:00Z")));
        assert!(w.is_over(utc("2026-03-08T07:00:00Z")));
    }

    #[test]
    fn an_unknown_zone_opens_earliest_and_closes_latest() {
        let w = window("2026-02-20", "2026-02-20", None);
        assert_eq!(
            w.phase(utc("2026-01-01T00:00:00Z")),
            Phase::Upcoming(utc("2026-02-19T16:00:00Z"))
        );
        assert!(!w.is_over(utc("2026-02-21T13:59:00Z")));
        assert!(w.is_over(utc("2026-02-21T14:00:00Z")));
    }

    #[test]
    fn warm_up_leads_the_first_match_of_that_day() {
        let w = window("2025-11-03", "2025-11-04", Some("America/New_York"));
        let starts = [
            "2025-11-04T09:00:00",
            "2025-11-03T19:12:00",
            "2025-11-03T18:00:00",
        ]
        .map(|s| s.parse().unwrap());
        assert_eq!(
            w.warm_up(day("2025-11-03"), starts),
            Some(utc("2025-11-03T22:30:00Z"))
        );
        assert_eq!(w.warm_up(day("2025-11-05"), starts), None);
    }

    #[test]
    fn no_zone_means_no_warm_up() {
        let w = window("2025-11-03", "2025-11-03", None);
        let starts = ["2025-11-03T18:00:00".parse().unwrap()];
        assert_eq!(w.warm_up(day("2025-11-03"), starts), None);
    }
}
