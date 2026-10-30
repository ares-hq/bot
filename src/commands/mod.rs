pub mod favorite;
pub mod help;
pub mod match_cmd;
pub mod respond;
pub mod subscribe;
pub mod team;
pub mod unfavorite;
pub mod unsubscribe;

use crate::bot_state::error_embed;
use crate::services::Services;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, Context, CreateAutocompleteResponse, CreateCommand, CreateEmbed,
    CreateInteractionResponse, Permissions,
};

/// Discord shows at most this many suggestions.
const MAX_SUGGESTIONS: usize = 25;

pub fn option_str<'a>(interaction: &'a CommandInteraction, name: &str) -> Option<&'a str> {
    interaction
        .data
        .options
        .iter()
        .find(|opt| opt.name == name)?
        .value
        .as_str()
}

pub fn can_manage_channels(interaction: &CommandInteraction) -> bool {
    interaction
        .member
        .as_ref()
        .and_then(|m| m.permissions)
        .is_some_and(|p| p.manage_channels())
}

/// What the bot needs in a channel to post a match card there.
pub fn bot_can_post(interaction: &CommandInteraction) -> bool {
    let needed = Permissions::VIEW_CHANNEL
        | Permissions::SEND_MESSAGES
        | Permissions::EMBED_LINKS
        | Permissions::ATTACH_FILES;
    interaction
        .app_permissions
        .is_some_and(|p| p.contains(needed))
}

pub fn server_only() -> CreateEmbed {
    error_embed("Server Only", "This command only works inside a server.")
}

pub fn needs_manage_channels(what: &str) -> CreateEmbed {
    error_embed(
        "Permission Required",
        &format!("Only members who can manage channels can change {what}."),
    )
}

pub fn cannot_post_here() -> CreateEmbed {
    error_embed(
        "Cannot Post Here",
        "ARES can't post here. Ask a server admin to let ARES send messages, embed links and attach files in this channel.",
    )
}

pub fn not_saved() -> CreateEmbed {
    error_embed(
        "Not Saved",
        "Something went wrong, so nothing was changed. Please try again in a moment.",
    )
}

/// Answers an autocomplete with the `(label, value)` pairs matching what was typed.
pub async fn suggest(
    ctx: &Context,
    interaction: &CommandInteraction,
    choices: impl IntoIterator<Item = (String, String)>,
) -> Result<()> {
    let typed = interaction
        .data
        .autocomplete()
        .map(|o| o.value.to_lowercase())
        .unwrap_or_default();
    let response = choices
        .into_iter()
        .filter(|(label, _)| label.to_lowercase().contains(&typed))
        .take(MAX_SUGGESTIONS)
        .fold(CreateAutocompleteResponse::new(), |r, (label, value)| {
            r.add_string_choice(label, value)
        });
    interaction
        .create_response(&ctx.http, CreateInteractionResponse::Autocomplete(response))
        .await?;
    Ok(())
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Command {
    Team,
    Match,
    Favorite,
    Unfavorite,
    Subscribe,
    Unsubscribe,
    Help,
}

impl Command {
    pub const ALL: [Command; 7] = [
        Command::Team,
        Command::Match,
        Command::Favorite,
        Command::Unfavorite,
        Command::Subscribe,
        Command::Unsubscribe,
        Command::Help,
    ];

    pub fn name(self) -> &'static str {
        match self {
            Command::Team => "team",
            Command::Match => "match",
            Command::Favorite => "favorite",
            Command::Unfavorite => "unfavorite",
            Command::Subscribe => "subscribe",
            Command::Unsubscribe => "unsubscribe",
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
            Command::Unfavorite => unfavorite::register(),
            Command::Subscribe => subscribe::register(),
            Command::Unsubscribe => unsubscribe::register(),
            Command::Help => help::register(),
        }
    }

    pub async fn run(
        self,
        ctx: &Context,
        interaction: &CommandInteraction,
        services: &Services,
    ) -> Result<()> {
        match self {
            Command::Team => {
                team::run(ctx, interaction, &services.teams, &services.favorites).await
            }
            Command::Match => match_cmd::run(ctx, interaction, &services.teams).await,
            Command::Favorite => favorite::run(ctx, interaction, services).await,
            Command::Unfavorite => unfavorite::run(ctx, interaction, services).await,
            Command::Subscribe => subscribe::run(ctx, interaction, services).await,
            Command::Unsubscribe => unsubscribe::run(ctx, interaction, services).await,
            Command::Help => help::run(ctx, interaction).await,
        }
    }

    pub async fn autocomplete(
        self,
        ctx: &Context,
        interaction: &CommandInteraction,
        services: &Services,
    ) -> Result<()> {
        match self {
            Command::Unfavorite => unfavorite::autocomplete(ctx, interaction, services).await,
            Command::Unsubscribe => unsubscribe::autocomplete(ctx, interaction, services).await,
            Command::Team
            | Command::Match
            | Command::Favorite
            | Command::Subscribe
            | Command::Help => Ok(()),
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
