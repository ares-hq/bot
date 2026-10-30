use crate::bot_state::{error_embed, success_embed, warning_embed};
use crate::commands::{
    can_manage_channels, needs_manage_channels, not_saved, option_str, respond, server_only,
    suggest,
};
use crate::live::RouteChange;
use crate::services::Services;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateCommand, CreateCommandOption,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    services: &Services,
) -> Result<()> {
    let Some(guild) = interaction.guild_id else {
        return respond::public(ctx, interaction, server_only()).await;
    };
    let Some(Ok(team)) =
        option_str(interaction, "team_number").map(|raw| raw.trim().parse::<u32>())
    else {
        let embed = error_embed("Invalid Team Number", "Enter a team number, like 14584.");
        return respond::ephemeral(ctx, interaction, embed).await;
    };
    if !can_manage_channels(interaction) {
        return respond::ephemeral(ctx, interaction, needs_manage_channels("favorites")).await;
    }

    let embed = match services.favorites.unfavorite(guild, team).await {
        Ok(true) => {
            services.route(RouteChange::Unfavorited { guild, team });
            success_embed(
                "Favorite Removed",
                &format!("Team {team} removed from favorites."),
            )
        }
        Ok(false) => warning_embed(
            "Not a Favorite",
            &format!("Team {team} isn't one of this server's favorites."),
        ),
        Err(err) => {
            tracing::error!(%guild, team, error = %err, "Could not remove favorite");
            return respond::ephemeral(ctx, interaction, not_saved()).await;
        }
    };
    respond::public(ctx, interaction, embed).await
}

/// Suggests this server's favorites, named when the team is known.
pub async fn autocomplete(
    ctx: &Context,
    interaction: &CommandInteraction,
    services: &Services,
) -> Result<()> {
    let Some(guild) = interaction.guild_id else {
        return Ok(());
    };
    let numbers: Vec<u32> = services
        .favorites
        .list_favorites(guild)
        .await?
        .into_iter()
        .map(|(number, _)| number)
        .collect();
    let known = services.teams.teams(&numbers).await.unwrap_or_default();

    let choices = numbers.into_iter().map(|number| {
        let label = match known.iter().find(|t| t.number == number) {
            Some(team) if !team.name.is_empty() => format!("{number} · {}", team.name),
            _ => format!("Team {number}"),
        };
        (label, number.to_string())
    });
    suggest(ctx, interaction, choices).await
}

pub fn register() -> CreateCommand {
    CreateCommand::new("unfavorite")
        .description("Stop following a team's match results.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "team_number",
                "One of this server's favorite teams.",
            )
            .required(true)
            .set_autocomplete(true),
        )
}
