use crate::bot_state::{Colors, DEVELOPERS, VERSION};
use anyhow::Result;
use serenity::all::{
    ButtonStyle, CommandInteraction, ComponentInteraction, Context, CreateActionRow, CreateButton,
    CreateCommand, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
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
             for example `12345 6789`. Omit the blue alliance to score the red one on its own.",
            false,
        ),
        1 => {
            base("Favorite teams are shared by everyone in the server and persist across restarts.")
                .field(
                    "/favorite <team_number>",
                    "Toggle a team: the first call adds it, the next removes it.",
                    false,
                )
                .field(
                    "/favorite",
                    "With no team number, lists every favorite in this server.",
                    false,
                )
                .field(
                    "Where favorites show up",
                    "A favorited team is marked with a star in its /team card.",
                    false,
                )
        }
        _ => base("Reading the numbers.")
            .field(
                "About OPR",
                "OPR (Offensive Power Rating) is a least-squares estimate of a team's average \
                 contribution to its alliance's score. ARES solves it per season for auto, \
                 teleop, endgame and penalties.",
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

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> Result<()> {
    let initial_page = 0;
    let embed = build_help_embed(initial_page);

    interaction
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .embed(embed)
                    .components(build_help_navigation(initial_page))
                    .ephemeral(true),
            ),
        )
        .await?;

    Ok(())
}

pub async fn handle_component(ctx: &Context, interaction: &ComponentInteraction) -> Result<bool> {
    let Some(raw_page) = interaction.data.custom_id.strip_prefix("help:page:") else {
        return Ok(false);
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

    Ok(true)
}

pub fn register() -> CreateCommand {
    CreateCommand::new("help").description("Show help information about ARES bot commands")
}
