use crate::bot_state::{Colors, error_embed, warning_embed};
use crate::image_generator::ImageGenerator;
use crate::match_data::Match;
use crate::teams::Teams;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateAttachment, CreateCommand,
    CreateCommandOption, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
};

pub async fn run(ctx: &Context, interaction: &CommandInteraction, teams: &Teams) -> Result<()> {
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

    let parse_alliance = |value: &str| -> Option<Vec<u32>> {
        let teams: Vec<u32> = value
            .split_whitespace()
            .filter_map(|s| s.parse::<u32>().ok())
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
    let match_result = Match::create(red_teams, blue_option, teams).await;

    match match_result {
        Ok(match_data) => {
            // Generate match image (PNG bytes)
            let bytes = if match_data.blue_alliance.is_empty() {
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

            let (red_total, blue_total) = match_data.totals();

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
                    format!("Total: {red_total:.0} points"),
                    true,
                )
                .field(
                    "Blue Alliance",
                    format!("Total: {blue_total:.0} points"),
                    true,
                )
                .image("attachment://match.png");

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
