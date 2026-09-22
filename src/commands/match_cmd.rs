use crate::bot_state::{Colors, error_embed, warning_embed};
use crate::commands::{option_str, respond};
use crate::image_generator::ImageGenerator;
use crate::match_data::{Match, Outcome};
use crate::team_store::TeamStore;
use anyhow::{Context as _, Result};
use model::prelude::Winner;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateAttachment, CreateCommand,
    CreateCommandOption, CreateEmbed,
};

const ALLIANCE_FORMAT: &str = "Each alliance must be exactly 2 team numbers separated by a space, \
                               for example `12345 6789`.";

fn parse_alliance(value: &str) -> Option<Vec<u32>> {
    let teams: Vec<u32> = value
        .split_whitespace()
        .map(str::parse)
        .collect::<Result<_, _>>()
        .ok()?;
    (teams.len() == 2).then_some(teams)
}

pub async fn run(ctx: &Context, interaction: &CommandInteraction, store: &TeamStore) -> Result<()> {
    let red_raw = option_str(interaction, "red_alliance")
        .ok_or_else(|| anyhow::anyhow!("red_alliance is required"))?;

    let Some(red_teams) = parse_alliance(red_raw) else {
        return respond::ephemeral(ctx, interaction, warning_embed("Warning", ALLIANCE_FORMAT))
            .await;
    };

    let blue_teams = match option_str(interaction, "blue_alliance").map(parse_alliance) {
        None => None,
        Some(Some(parsed)) => Some(parsed),
        Some(None) => {
            return respond::ephemeral(ctx, interaction, warning_embed("Warning", ALLIANCE_FORMAT))
                .await;
        }
    };

    respond::defer(ctx, interaction).await?;

    let match_data = match Match::create(red_teams, blue_teams, store).await {
        Ok(match_data) => match_data,
        Err(err) => {
            tracing::error!(error = %err, "Could not assemble match");
            let embed = error_embed("Match Error", "Could not look those teams up.");
            return respond::edit(ctx, interaction, embed).await;
        }
    };

    let (red, blue) = (
        match_data.red_alliance.clone(),
        match_data.blue_alliance.clone(),
    );
    let rendered = tokio::task::spawn_blocking(move || {
        if blue.is_empty() {
            ImageGenerator::create_alliance_image(&red)
        } else {
            ImageGenerator::create_match_image(&red, &blue)
        }
    })
    .await
    .context("card renderer panicked")?;

    let bytes = match rendered {
        Ok(bytes) => bytes,
        Err(err) => {
            tracing::error!(error = %err, "Could not render match card");
            let embed = error_embed("Render Failed", "Could not draw the match card.");
            return respond::edit(ctx, interaction, embed).await;
        }
    };

    let outcome = match_data.outcome();
    let (red_total, blue_total) = match_data.totals();

    let embed = CreateEmbed::new()
        .title("Match Scoreboard")
        .color(match outcome {
            Outcome::Won(Winner::Red) => Colors::CHALLENGE_RED,
            Outcome::Won(Winner::Blue) => Colors::FIRST_BLUE,
            _ => Colors::WHITE,
        })
        .description(match outcome {
            Outcome::Won(Winner::Red) => "Red Alliance Wins!",
            Outcome::Won(Winner::Blue) => "Blue Alliance Wins!",
            Outcome::Tie => "Tie Match!",
            Outcome::Incomplete => "Match Incomplete",
        })
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

    respond::edit_with_attachment(
        ctx,
        interaction,
        embed,
        CreateAttachment::bytes(bytes, "match.png"),
    )
    .await
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_pair_of_numbers_parses() {
        assert_eq!(parse_alliance("12345 6789"), Some(vec![12345, 6789]));
        assert_eq!(parse_alliance("  12345   6789  "), Some(vec![12345, 6789]));
    }

    #[test]
    fn the_wrong_count_is_rejected() {
        assert_eq!(parse_alliance("12345"), None);
        assert_eq!(parse_alliance("1 2 3"), None);
        assert_eq!(parse_alliance(""), None);
    }

    #[test]
    fn a_stray_word_is_rejected_rather_than_skipped() {
        assert_eq!(parse_alliance("12345 oops 6789"), None);
        assert_eq!(parse_alliance("12345 -1"), None);
    }
}
