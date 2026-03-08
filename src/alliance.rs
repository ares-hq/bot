use crate::supabase_handler::TeamData;

#[derive(Debug, Clone)]
pub enum AllianceColor {
    Red,
    Blue,
}

impl AllianceColor {
    pub fn as_str(&self) -> &str {
        match self {
            AllianceColor::Red => "Red",
            AllianceColor::Blue => "Blue",
        }
    }
}

#[derive(Debug, Clone)]
pub struct AllianceScore {
    pub auto: f64,
    pub teleop: f64,
    pub endgame: f64,
    pub penalties: f64,
    pub total: f64,
}

#[derive(Debug, Clone)]
pub struct Alliance {
    pub team1: Option<TeamData>,
    pub team2: Option<TeamData>,
    pub color: AllianceColor,
}

impl Alliance {
    pub fn new(team1: Option<TeamData>, team2: Option<TeamData>, color: AllianceColor) -> Self {
        Self {
            team1,
            team2,
            color,
        }
    }

    pub fn team_names(&self) -> Vec<String> {
        let mut names = Vec::new();
        if let Some(team) = &self.team1 {
            names.push(team.team_name.clone());
        } else {
            names.push(String::new());
        }
        if let Some(team) = &self.team2 {
            names.push(team.team_name.clone());
        } else {
            names.push(String::new());
        }
        names
    }

    pub fn team_numbers(&self) -> Vec<i32> {
        let mut numbers = Vec::new();
        if let Some(team) = &self.team1 {
            numbers.push(team.team_number);
        }
        if let Some(team) = &self.team2 {
            numbers.push(team.team_number);
        }
        numbers
    }

    pub fn calculate_score(&self) -> AllianceScore {
        let auto = self.team1.as_ref().map(|t| t.auto_opr).unwrap_or(0.0)
            + self.team2.as_ref().map(|t| t.auto_opr).unwrap_or(0.0);

        let teleop = self.team1.as_ref().map(|t| t.tele_opr).unwrap_or(0.0)
            + self.team2.as_ref().map(|t| t.tele_opr).unwrap_or(0.0);

        let endgame = self.team1.as_ref().map(|t| t.endgame_opr).unwrap_or(0.0)
            + self.team2.as_ref().map(|t| t.endgame_opr).unwrap_or(0.0);

        let penalties = self.team1.as_ref().map(|t| t.penalties).unwrap_or(0.0)
            + self.team2.as_ref().map(|t| t.penalties).unwrap_or(0.0);

        let total = auto + teleop + endgame;

        AllianceScore {
            auto,
            teleop,
            endgame,
            penalties,
            total,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.team1.is_none() && self.team2.is_none()
    }
}
