use crate::alliance::Alliance;
use crate::team_store::TeamStore;
use anyhow::Result;
use model::prelude::{Match as Scored, Winner};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Outcome {
    Incomplete,
    Tie,
    Won(Winner),
}

pub struct Match {
    pub red_alliance: Alliance,
    pub blue_alliance: Alliance,
}

impl Match {
    pub async fn create(
        red_teams: Vec<u32>,
        blue_teams: Option<Vec<u32>>,
        store: &TeamStore,
    ) -> Result<Self> {
        let blue_numbers = blue_teams.unwrap_or_default();
        let wanted: Vec<u32> = red_teams
            .iter()
            .chain(blue_numbers.iter())
            .copied()
            .collect();

        let found = store.teams(&wanted).await?;
        let pick = |number: u32| found.iter().find(|t| t.number == number).cloned();
        let alliance = |numbers: &[u32]| match numbers {
            [a, b] => Alliance::new(pick(*a), pick(*b)),
            _ => Alliance::default(),
        };

        Ok(Self {
            red_alliance: alliance(&red_teams),
            blue_alliance: alliance(&blue_numbers),
        })
    }

    pub fn to_scored(&self) -> Scored {
        Scored::new((&self.red_alliance).into(), (&self.blue_alliance).into())
    }

    pub fn totals(&self) -> (f64, f64) {
        self.to_scored().totals()
    }

    pub fn outcome(&self) -> Outcome {
        if self.blue_alliance.is_empty() {
            return Outcome::Incomplete;
        }
        match self.to_scored().winner() {
            Some(winner) => Outcome::Won(winner),
            None => Outcome::Tie,
        }
    }
}
