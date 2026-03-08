use crate::bot_state::{Colors, error_embed, warning_embed};
use crate::favorites::FavoritesManager;
use crate::supabase_handler::SupabaseHandler;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, Context, CreateCommand, CreateEmbed, CreateInteractionResponse,
    CreateInteractionResponseMessage,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    supabase: &SupabaseHandler,
    favorites: &FavoritesManager,
) -> Result<()> {
    let team_number_raw = interaction
        .data
        .options
        .iter()
        .find(|opt| opt.name == "team_number")
        .and_then(|opt| opt.value.as_str())
        .ok_or_else(|| anyhow::anyhow!("Team number is required"))?;

    let team_number: i32 = match team_number_raw.parse() {
        Ok(v) => v,
        Err(_) => {
            let embed = warning_embed("Warning", "Team number must be numerical.");
            interaction
                .create_response(
                    &ctx.http,
                    CreateInteractionResponse::Message(
                        CreateInteractionResponseMessage::new()
                            .embed(embed)
                            .ephemeral(true),
                    ),
                )
                .await?;
            return Ok(());
        }
    };

    // Acknowledge the interaction
    interaction
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Defer(CreateInteractionResponseMessage::new()),
        )
        .await?;

    // Fetch team data
    let team_result = supabase.get_team(team_number).await;

    match team_result {
        Ok(team) => {
            let is_favorite = if let Some(guild_id) = interaction.guild_id {
                favorites.is_favorite(guild_id, team_number)
            } else {
                false
            };

            let star = if is_favorite { "⭐" } else { "" };
            let title = format!("{} Team {} - {}", star, team.team_number, team.team_name);

            let location = team.location.as_deref().unwrap_or("Unknown");
            let sponsors = team.sponsors.as_deref().unwrap_or("None listed");

            let embed = CreateEmbed::new()
                .title(title)
                .color(Colors::FIRST_BLUE)
                .field("Team Number", team.team_number.to_string(), true)
                .field("Team Name", &team.team_name, true)
                .field("Location", location, true)
                .field("", "", false)
                .field("Auto OPR", format!("{:.2}", team.auto_opr), true)
                .field("TeleOp OPR", format!("{:.2}", team.tele_opr), true)
                .field("Endgame OPR", format!("{:.2}", team.endgame_opr), true)
                .field("Overall OPR", format!("{:.2}", team.overall_opr), true)
                .field("Penalties", format!("{:.2}", team.penalties), true)
                .field("", "", true)
                .field("Sponsors", sponsors, false)
                .footer(serenity::all::CreateEmbedFooter::new(format!(
                    "Rank: #{}",
                    team.overall_rank.unwrap_or(0)
                )));

            interaction
                .edit_response(
                    &ctx.http,
                    serenity::all::EditInteractionResponse::new().embed(embed),
                )
                .await?;
        }
        Err(e) => {
            let embed = error_embed(
                "Team Not Found",
                &format!("Could not find team {}: {}", team_number, e),
            );

            interaction
                .edit_response(
                    &ctx.http,
                    serenity::all::EditInteractionResponse::new().embed(embed),
                )
                .await?;
        }
    }

    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("team")
        .description("Displays team information.")
        .add_option(
            serenity::all::CreateCommandOption::new(
                serenity::all::CommandOptionType::String,
                "team_number",
                "Details about the team.",
            )
            .required(true),
        )
}
