use crate::bot_state::{Colors, error_embed, warning_embed};
use crate::commands::{Context, respond};
use crate::image_generator::ImageGenerator;
use crate::match_data::{Match, Outcome};
use anyhow::{Context as _, Result};
use model::prelude::Winner;
use serenity::all::{CreateAttachment, CreateEmbed};

const ALLIANCE_FORMAT: &str = "Each alliance must be exactly 2 team numbers separated by a space, \
                               for example `14584 6789`.";

fn parse_alliance(value: &str) -> Option<Vec<u32>> {
    let teams: Vec<u32> = value
        .split_whitespace()
        .map(str::parse)
        .collect::<Result<_, _>>()
        .ok()?;
    (teams.len() == 2).then_some(teams)
}

/// Displays match details.
#[poise::command(slash_command, rename = "match")]
pub async fn simulate(
    ctx: Context<'_>,
    #[description = "Red Alliance team numbers (space-separated)."] red_alliance: String,
    #[description = "Blue Alliance team numbers (space-separated, optional)."]
    blue_alliance: Option<String>,
) -> Result<()> {
    let Some(red_teams) = parse_alliance(&red_alliance) else {
        return respond::ephemeral(ctx, warning_embed("Check Your Teams", ALLIANCE_FORMAT)).await;
    };
    let blue_teams = match blue_alliance.as_deref().map(parse_alliance) {
        None => None,
        Some(Some(parsed)) => Some(parsed),
        Some(None) => {
            return respond::ephemeral(ctx, warning_embed("Check Your Teams", ALLIANCE_FORMAT))
                .await;
        }
    };

    ctx.defer().await?;

    let match_data = match Match::create(red_teams, blue_teams, &ctx.data().teams).await {
        Ok(match_data) => match_data,
        Err(err) => {
            tracing::error!(error = %err, "Could not assemble match");
            let embed = error_embed(
                "Teams Unavailable",
                "Couldn't look those teams up right now. Please try again in a moment.",
            );
            return respond::public(ctx, embed).await;
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
            let embed = error_embed(
                "Something Went Wrong",
                "Couldn't make the match card. Please try again in a moment.",
            );
            return respond::public(ctx, embed).await;
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

    respond::with_attachment(ctx, embed, CreateAttachment::bytes(bytes, "match.png")).await
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_pair_of_numbers_parses() {
        assert_eq!(parse_alliance("14584 6789"), Some(vec![14584, 6789]));
        assert_eq!(parse_alliance("  14584   6789  "), Some(vec![14584, 6789]));
    }

    #[test]
    fn the_wrong_count_is_rejected() {
        assert_eq!(parse_alliance("14584"), None);
        assert_eq!(parse_alliance("1 2 3"), None);
        assert_eq!(parse_alliance(""), None);
    }

    #[test]
    fn a_stray_word_is_rejected_rather_than_skipped() {
        assert_eq!(parse_alliance("14584 oops 6789"), None);
        assert_eq!(parse_alliance("14584 -1"), None);
    }
}
