use model::prelude::{Alliance as Scores, Team};

#[derive(Debug, Clone, Default)]
pub struct Alliance {
    pub teams: [Option<Team>; 2],
}

impl Alliance {
    pub fn new(team1: Option<Team>, team2: Option<Team>) -> Self {
        Self {
            teams: [team1, team2],
        }
    }

    pub fn team(&self, slot: usize) -> Option<&Team> {
        self.teams.get(slot).and_then(Option::as_ref)
    }

    pub fn is_empty(&self) -> bool {
        self.teams.iter().all(Option::is_none)
    }
}

impl From<&Alliance> for Scores {
    fn from(alliance: &Alliance) -> Self {
        let sum = |pick: fn(&Team) -> f64| alliance.teams.iter().flatten().map(pick).sum();

        Scores {
            teams: [
                alliance.team(0).map_or(0, |t| t.number),
                alliance.team(1).map_or(0, |t| t.number),
            ],
            auto: sum(|t| t.auto),
            teleop: sum(|t| t.teleop),
            endgame: sum(|t| t.endgame),
            penalties: sum(|t| t.penalties),
        }
    }
}
