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
use poise::FrameworkError;
use serenity::all::{CommandInteraction, CreateEmbed, Permissions};
use std::sync::Arc;

pub type Error = anyhow::Error;
pub type Context<'a> = poise::Context<'a, Arc<Services>, Error>;
pub type Command = poise::Command<Arc<Services>, Error>;

/// Discord shows at most this many suggestions.
const MAX_SUGGESTIONS: usize = 25;

pub fn all() -> Vec<Command> {
    vec![
        team::team(),
        match_cmd::simulate(),
        favorite::favorite(),
        unfavorite::unfavorite(),
        subscribe::subscribe(),
        unsubscribe::unsubscribe(),
        help::help(),
    ]
}

fn interaction(ctx: Context<'_>) -> Option<&CommandInteraction> {
    match ctx {
        poise::Context::Application(app) => Some(app.interaction),
        poise::Context::Prefix(_) => None,
    }
}

pub fn can_manage_channels(ctx: Context<'_>) -> bool {
    interaction(ctx)
        .and_then(|i| i.member.as_ref()?.permissions)
        .is_some_and(|p| p.manage_channels())
}

/// What the bot needs in a channel to post a match card there.
pub fn bot_can_post(ctx: Context<'_>) -> bool {
    let needed = Permissions::VIEW_CHANNEL
        | Permissions::SEND_MESSAGES
        | Permissions::EMBED_LINKS
        | Permissions::ATTACH_FILES;
    interaction(ctx)
        .and_then(|i| i.app_permissions)
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

/// The `(label, value)` pairs whose label contains what was typed.
pub fn matching<T>(
    typed: &str,
    choices: impl IntoIterator<Item = (String, T)>,
) -> impl Iterator<Item = (String, T)> {
    let typed = typed.to_lowercase();
    choices
        .into_iter()
        .filter(move |(label, _)| label.to_lowercase().contains(&typed))
        .take(MAX_SUGGESTIONS)
}

/// In debug mode, answers only in the development channels.
pub async fn allowed_here(ctx: Context<'_>) -> Result<bool> {
    let Some(allowed) = &ctx.data().debug_channels else {
        return Ok(true);
    };
    if allowed.contains(&ctx.channel_id()) {
        return Ok(true);
    }
    let embed = error_embed(
        "Not Available Here",
        "ARES is being updated and only answers in certain channels right now.",
    );
    respond::ephemeral(ctx, embed).await?;
    Ok(false)
}

pub async fn on_error(error: FrameworkError<'_, Arc<Services>, Error>) {
    let reply = match error {
        FrameworkError::Command { error, ctx, .. } => {
            tracing::error!(command = %ctx.command().name, error = %error, "Command failed");
            return;
        }
        FrameworkError::GuildOnly { ctx, .. } => respond::ephemeral(ctx, server_only()).await,
        FrameworkError::ArgumentParse { ctx, .. } => {
            let embed = error_embed(
                "Check Your Input",
                "That doesn't look right. Please try again.",
            );
            respond::ephemeral(ctx, embed).await
        }
        FrameworkError::CommandCheckFailed { error: None, .. } => return,
        other => {
            tracing::error!(error = %other, "Command could not run");
            return;
        }
    };
    if let Err(err) = reply {
        tracing::error!(error = %err, "Could not answer a failed command");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_command_has_a_unique_name() {
        let mut names: Vec<String> = all().into_iter().map(|c| c.name.into_owned()).collect();
        let count = names.len();
        names.sort_unstable();
        names.dedup();
        assert_eq!(names.len(), count);
        assert!(names.iter().any(|n| n == "match"));
    }

    #[test]
    fn every_description_fits_discord() {
        for command in all() {
            let description = command.description.unwrap_or_default();
            assert!(
                (1..=100).contains(&description.len()),
                "/{}: {description:?}",
                command.name
            );
            for param in command.parameters {
                let description = param.description.unwrap_or_default();
                assert!((1..=100).contains(&description.len()), "{}", param.name);
            }
        }
    }

    #[test]
    fn suggestions_match_case_insensitively_and_cap_at_the_limit() {
        let choices = (0..40).map(|n| (format!("Team {n}"), n));
        assert_eq!(matching("team", choices).count(), MAX_SUGGESTIONS);
        let picked: Vec<_> = matching("PIONEER", [("14584 · Pioneer 327".to_owned(), 14584)])
            .map(|(_, n)| n)
            .collect();
        assert_eq!(picked, [14584]);
    }
}
