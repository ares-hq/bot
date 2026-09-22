pub mod favorite;
pub mod help;
pub mod match_cmd;
pub mod respond;
pub mod team;

use crate::favorites::FavoritesManager;
use crate::team_store::TeamStore;
use anyhow::Result;
use serenity::all::{CommandInteraction, Context, CreateCommand};

pub fn option_str<'a>(interaction: &'a CommandInteraction, name: &str) -> Option<&'a str> {
    interaction
        .data
        .options
        .iter()
        .find(|opt| opt.name == name)?
        .value
        .as_str()
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Command {
    Team,
    Match,
    Favorite,
    Help,
}

impl Command {
    pub const ALL: [Command; 4] = [
        Command::Team,
        Command::Match,
        Command::Favorite,
        Command::Help,
    ];

    pub fn name(self) -> &'static str {
        match self {
            Command::Team => "team",
            Command::Match => "match",
            Command::Favorite => "favorite",
            Command::Help => "help",
        }
    }

    pub fn from_name(name: &str) -> Option<Command> {
        Command::ALL.into_iter().find(|c| c.name() == name)
    }

    pub fn register(self) -> CreateCommand {
        match self {
            Command::Team => team::register(),
            Command::Match => match_cmd::register(),
            Command::Favorite => favorite::register(),
            Command::Help => help::register(),
        }
    }

    pub async fn run(
        self,
        ctx: &Context,
        interaction: &CommandInteraction,
        store: &TeamStore,
        favorites: &FavoritesManager,
    ) -> Result<()> {
        match self {
            Command::Team => team::run(ctx, interaction, store, favorites).await,
            Command::Match => match_cmd::run(ctx, interaction, store).await,
            Command::Favorite => favorite::run(ctx, interaction, favorites).await,
            Command::Help => help::run(ctx, interaction).await,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_command_round_trips_through_its_name() {
        for command in Command::ALL {
            assert_eq!(Command::from_name(command.name()), Some(command));
        }
    }

    #[test]
    fn names_are_unique() {
        let mut names: Vec<&str> = Command::ALL.iter().map(|c| c.name()).collect();
        names.sort_unstable();
        let count = names.len();
        names.dedup();
        assert_eq!(names.len(), count);
    }

    #[test]
    fn an_unknown_name_has_no_command() {
        assert_eq!(Command::from_name("nope"), None);
    }
}
