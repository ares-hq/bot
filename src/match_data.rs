use crate::alliance::{Alliance, AllianceColor};
use crate::teams::Teams;
use anyhow::Result;

pub struct Match {
    pub red_alliance: Alliance,
    pub blue_alliance: Alliance,
}

impl Match {
    pub async fn create(
        red_teams: Vec<u32>,
        blue_teams: Option<Vec<u32>>,
        teams: &Teams,
    ) -> Result<Self> {
        let red_alliance = Self::form_alliance(red_teams, AllianceColor::Red, teams).await?;

        let blue_alliance = if let Some(blue) = blue_teams {
            Self::form_alliance(blue, AllianceColor::Blue, teams).await?
        } else {
            Alliance::new(None, None, AllianceColor::Blue)
        };

        Ok(Self {
            red_alliance,
            blue_alliance,
        })
    }

    async fn form_alliance(
        team_numbers: Vec<u32>,
        color: AllianceColor,
        teams: &Teams,
    ) -> Result<Alliance> {
        if team_numbers.len() != 2 {
            return Ok(Alliance::new(None, None, color));
        }

        let team1 = teams.get_team(team_numbers[0]).await.ok();
        let team2 = teams.get_team(team_numbers[1]).await.ok();

        Ok(Alliance::new(team1, team2, color))
    }

    /// `(red, blue)` totals: own auto+teleop+endgame plus the opponent's fouls.
    pub fn totals(&self) -> (f64, f64) {
        let r = self.red_alliance.calculate_score();
        let b = self.blue_alliance.calculate_score();
        (r.total + b.penalties, b.total + r.penalties)
    }

    pub fn winner(&self) -> &str {
        if self.blue_alliance.is_empty() {
            return "N/A";
        }

        let (red_score, blue_score) = self.totals();

        if (red_score - blue_score).abs() < 0.01 {
            "Tie"
        } else if red_score > blue_score {
            "Red"
        } else {
            "Blue"
        }
    }

    pub fn is_full_match(&self) -> bool {
        !self.blue_alliance.is_empty()
    }
}
