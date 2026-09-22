use crate::bot_state::{Colors, error_embed, warning_embed};
use crate::commands::{option_str, respond};
use crate::favorites::FavoritesManager;
use crate::team_store::TeamStore;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateCommand, CreateCommandOption,
    CreateEmbed, CreateEmbedFooter,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    store: &TeamStore,
    favorites: &FavoritesManager,
) -> Result<()> {
    let raw = option_str(interaction, "team_number")
        .ok_or_else(|| anyhow::anyhow!("team_number is required"))?;

    let Ok(team_number) = raw.parse::<u32>() else {
        let embed = warning_embed("Warning", "Team number must be numerical.");
        return respond::ephemeral(ctx, interaction, embed).await;
    };

    respond::defer(ctx, interaction).await?;

    let team = match store.team(team_number).await {
        Ok(team) => team,
        Err(err) => {
            tracing::warn!(team_number, error = %err, "Team lookup failed");
            let embed = error_embed(
                "Team Not Found",
                &format!("Could not find team {team_number} in this season's data."),
            );
            return respond::edit(ctx, interaction, embed).await;
        }
    };

    let starred = match interaction.guild_id {
        Some(guild_id) => favorites.is_favorite(guild_id, team_number).await,
        None => false,
    };

    let or_unknown = |value: &str, fallback: &'static str| {
        if value.is_empty() {
            fallback.to_owned()
        } else {
            value.to_owned()
        }
    };

    let embed = CreateEmbed::new()
        .title(format!(
            "{}Team {} - {}",
            if starred { "⭐ " } else { "" },
            team.number,
            team.name
        ))
        .color(Colors::FIRST_BLUE)
        .field("Team Number", team.number.to_string(), true)
        .field("Team Name", &team.name, true)
        .field("Location", or_unknown(&team.location, "Unknown"), true)
        .field("", "", false)
        .field("Auto OPR", format!("{:.2}", team.auto), true)
        .field("TeleOp OPR", format!("{:.2}", team.teleop), true)
        .field("Endgame OPR", format!("{:.2}", team.endgame), true)
        .field("Overall OPR", format!("{:.2}", team.overall), true)
        .field("Penalties", format!("{:.2}", team.penalties), true)
        .field("", "", true)
        .field("Sponsors", or_unknown(&team.sponsors, "None listed"), false)
        .footer(CreateEmbedFooter::new(match team.overall_rank {
            Some(rank) => format!("Rank: #{rank}"),
            None => "Unranked".to_owned(),
        }));

    respond::edit(ctx, interaction, embed).await
}

pub fn register() -> CreateCommand {
    CreateCommand::new("team")
        .description("Displays team information.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "team_number",
                "Details about the team.",
            )
            .required(true),
        )
}
