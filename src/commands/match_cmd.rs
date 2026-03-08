use crate::bot_state::{Colors, error_embed, warning_embed};
use crate::image_generator::ImageGenerator;
use crate::match_data::Match;
use crate::supabase_handler::SupabaseHandler;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateAttachment, CreateCommand,
    CreateCommandOption, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    supabase: &SupabaseHandler,
) -> Result<()> {
    let red_alliance_raw = interaction
        .data
        .options
        .iter()
        .find(|opt| opt.name == "red_alliance")
        .and_then(|opt| opt.value.as_str())
        .ok_or_else(|| anyhow::anyhow!("red_alliance is required"))?;

    let blue_alliance_raw = interaction
        .data
        .options
        .iter()
        .find(|opt| opt.name == "blue_alliance")
        .and_then(|opt| opt.value.as_str());

    let parse_alliance = |value: &str| -> Option<Vec<i32>> {
        let teams: Vec<i32> = value
            .split_whitespace()
            .filter_map(|s| s.parse::<i32>().ok())
            .collect();
        if teams.len() == 2 { Some(teams) } else { None }
    };

    let red_teams = match parse_alliance(red_alliance_raw) {
        Some(v) => v,
        None => {
            let embed = warning_embed(
                "Warning",
                "Each alliance must have exactly 2 team numbers separated by a space.",
            );
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

    let blue_option = match blue_alliance_raw {
        Some(raw) => match parse_alliance(raw) {
            Some(v) => Some(v),
            None => {
                let embed = warning_embed(
                    "Warning",
                    "Each alliance must have exactly 2 team numbers separated by a space.",
                );
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
        },
        None => None,
    };

    // Defer the response since this might take a while
    interaction
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Defer(CreateInteractionResponseMessage::new()),
        )
        .await?;

    // Create match data
    let match_result = Match::create(red_teams, blue_option, supabase).await;

    match match_result {
        Ok(match_data) => {
            // Generate match image
            let image = if match_data.blue_alliance.is_empty() {
                ImageGenerator::create_alliance_image(&match_data.red_alliance)
            } else {
                ImageGenerator::create_match_image(
                    &match_data.red_alliance,
                    &match_data.blue_alliance,
                )
            };

            let winner_text = match match_data.winner() {
                "Red" => "Red Alliance Wins!",
                "Blue" => "Blue Alliance Wins!",
                "Tie" => "Tie Match!",
                _ => "Match Incomplete",
            };

            let red_score = match_data.red_alliance.calculate_score();
            let blue_score = match_data.blue_alliance.calculate_score();

            let embed = CreateEmbed::new()
                .title("Match Scoreboard")
                .color(match match_data.winner() {
                    "Red" => Colors::CHALLENGE_RED,
                    "Blue" => Colors::FIRST_BLUE,
                    _ => Colors::WHITE,
                })
                .description(winner_text)
                .field(
                    "Red Alliance",
                    format!("Total: {} points", red_score.total),
                    true,
                )
                .field(
                    "Blue Alliance",
                    format!("Total: {} points", blue_score.total),
                    true,
                )
                .image("attachment://match.png");

            // Convert image to PNG bytes
            let mut bytes: Vec<u8> = Vec::new();
            image.write_to(
                &mut std::io::Cursor::new(&mut bytes),
                image::ImageFormat::Png,
            )?;
            let attachment = CreateAttachment::bytes(bytes, "match.png");

            interaction
                .edit_response(
                    &ctx.http,
                    serenity::all::EditInteractionResponse::new()
                        .embed(embed)
                        .new_attachment(attachment),
                )
                .await?;
        }
        Err(e) => {
            let embed = error_embed("Match Error", &format!("Failed to create match: {}", e));
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
    CreateCommand::new("match")
        .description("Displays match details.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "red_alliance",
                "Red Alliance team numbers (space-separated).",
            )
            .required(true),
        )
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "blue_alliance",
                "Blue Alliance team numbers (space-separated, optional).",
            )
            .required(false),
        )
}
