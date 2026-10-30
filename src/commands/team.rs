use crate::bot_state::{Colors, error_embed};
use crate::commands::{Context, respond};
use anyhow::Result;
use serenity::all::{CreateEmbed, CreateEmbedFooter};

/// Displays team information.
#[poise::command(slash_command)]
pub async fn team(
    ctx: Context<'_>,
    #[description = "Team number, like 14584."]
    #[min = 1]
    team_number: u32,
) -> Result<()> {
    ctx.defer().await?;
    let services = ctx.data();

    let team = match services.teams.team(team_number).await {
        Ok(team) => team,
        Err(err) => {
            tracing::warn!(team_number, error = %err, "Team lookup failed");
            let embed = error_embed(
                "Team Not Found",
                &format!("Couldn't find team {team_number} this season."),
            );
            return respond::public(ctx, embed).await;
        }
    };

    let starred = match ctx.guild_id() {
        Some(guild_id) => services.favorites.is_favorite(guild_id, team_number).await,
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

    respond::public(ctx, embed).await
}
