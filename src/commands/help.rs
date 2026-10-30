use crate::bot_state::{Colors, DEVELOPERS, VERSION};
use crate::commands::Context;
use anyhow::Result;
use poise::CreateReply;
use serenity::all::{
    ButtonStyle, ComponentInteraction, CreateActionRow, CreateButton, CreateEmbed,
    CreateInteractionResponse, CreateInteractionResponseMessage,
};

const HELP_TOTAL_PAGES: usize = 3;

fn build_help_embed(page: usize) -> CreateEmbed {
    let base = |description: &str| {
        CreateEmbed::new()
            .title(format!("ARES Bot Help {VERSION}"))
            .color(Colors::FIRST_BLUE)
            .description(description.to_owned())
            .footer(serenity::all::CreateEmbedFooter::new(format!(
                "Page {}/{HELP_TOTAL_PAGES}",
                page.min(HELP_TOTAL_PAGES - 1) + 1
            )))
    };

    match page {
        0 => base(
            "ARES (Analytical Robotics Evaluation System) provides FTC team statistics \
             and match simulations.",
        )
        .field(
            "/team <team_number>",
            "Season OPR breakdown, location, sponsors and overall rank for one team.",
            false,
        )
        .field(
            "/match <red_alliance> [blue_alliance]",
            "Simulate a matchup. Each alliance is two team numbers separated by a space, \
             for example `14584 6789`. Omit the blue alliance to score the red one on its own.",
            false,
        ),
        1 => {
            base("Favorites and subscriptions are shared by everyone in the server. Only members who can manage channels can change them.")
                .field(
                    "/favorite [team_number]",
                    "Follow a team: each of its match results posts in this channel. \
                     Use it in another channel to move it there. With no number, lists this server's favorites.",
                    false,
                )
                .field("/unfavorite <team_number>", "Stop following a team.", false)
                .field(
                    "/subscribe [event_code]",
                    "Follow an event: every match result posts in this channel. Use it in \
                     another channel to move it there. With no code, lists this server's events.",
                    false,
                )
                .field("/unsubscribe <event_code>", "Stop following an event.", false)
                .field(
                    "Where favorites show up",
                    "A favorited team gets a star on its /team card. Match results usually post \
                     within a minute of the official score.",
                    false,
                )
        }
        _ => base("Reading the numbers.")
            .field(
                "About OPR",
                "OPR (Offensive Power Rating) estimates how many points a team adds to its \
                 alliance's score in an average match. ARES works it out at every event and \
                 shows each team's best event this season, for auto, teleop, endgame and penalties.",
                false,
            )
            .field(
                "Overall OPR",
                "Auto plus teleop. Endgame and penalties are ranked separately.",
                false,
            )
            .field("/help", "Show this help message.", false)
            .field(
                "Support",
                format!("For issues or questions, contact the developers: {DEVELOPERS}"),
                false,
            ),
    }
}

fn build_help_navigation(page: usize) -> Vec<CreateActionRow> {
    let prev_page = page.saturating_sub(1);
    let at_last = page + 1 >= HELP_TOTAL_PAGES;
    let next_page = if at_last {
        HELP_TOTAL_PAGES - 1
    } else {
        page + 1
    };

    vec![CreateActionRow::Buttons(vec![
        CreateButton::new(format!("help:page:{}", prev_page))
            .label("Previous")
            .style(ButtonStyle::Secondary)
            .disabled(page == 0),
        CreateButton::new(format!("help:page:{}", next_page))
            .label("Next")
            .style(ButtonStyle::Primary)
            .disabled(at_last),
    ])]
}

/// Show help information about ARES bot commands
#[poise::command(slash_command)]
pub async fn help(ctx: Context<'_>) -> Result<()> {
    let reply = CreateReply::default()
        .embed(build_help_embed(0))
        .components(build_help_navigation(0))
        .ephemeral(true);
    ctx.send(reply).await?;
    Ok(())
}

pub async fn handle_component(
    ctx: &serenity::all::Context,
    interaction: &ComponentInteraction,
) -> Result<()> {
    let Some(raw_page) = interaction.data.custom_id.strip_prefix("help:page:") else {
        return Ok(());
    };

    let page = raw_page
        .parse::<usize>()
        .ok()
        .map(|v| v.min(HELP_TOTAL_PAGES - 1))
        .unwrap_or(0);

    interaction
        .create_response(
            &ctx.http,
            CreateInteractionResponse::UpdateMessage(
                CreateInteractionResponseMessage::new()
                    .embed(build_help_embed(page))
                    .components(build_help_navigation(page)),
            ),
        )
        .await?;

    Ok(())
}
