use crate::alliance::{Alliance, AllianceColor};
use crate::supabase_handler::{SupabaseHandler, TeamData};
use anyhow::{Context, Result};

pub struct Match {
    pub red_alliance: Alliance,
    pub blue_alliance: Alliance,
}

impl Match {
    pub async fn create(
        red_teams: Vec<i32>,
        blue_teams: Option<Vec<i32>>,
        handler: &SupabaseHandler,
    ) -> Result<Self> {
        let red_alliance = Self::form_alliance(red_teams, AllianceColor::Red, handler).await?;

        let blue_alliance = if let Some(blue) = blue_teams {
            Self::form_alliance(blue, AllianceColor::Blue, handler).await?
        } else {
            Alliance::new(None, None, AllianceColor::Blue)
        };

        Ok(Self {
            red_alliance,
            blue_alliance,
        })
    }

    async fn form_alliance(
        team_numbers: Vec<i32>,
        color: AllianceColor,
        handler: &SupabaseHandler,
    ) -> Result<Alliance> {
        if team_numbers.len() != 2 {
            return Ok(Alliance::new(None, None, color));
        }

        let team1 = handler.get_team(team_numbers[0]).await.ok();
        let team2 = handler.get_team(team_numbers[1]).await.ok();

        Ok(Alliance::new(team1, team2, color))
    }

    pub fn winner(&self) -> &str {
        if self.blue_alliance.is_empty() {
            return "N/A";
        }

        let red_score = self.red_alliance.calculate_score().total;
        let blue_score = self.blue_alliance.calculate_score().total;

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
