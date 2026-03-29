use crate::bot_state::{Colors, DEVELOPERS, VERSION};
use anyhow::Result;
use serenity::all::{
    ButtonStyle, CommandInteraction, ComponentInteraction, Context, CreateActionRow,
    CreateButton, CreateCommand, CreateEmbed, CreateInteractionResponse,
    CreateInteractionResponseMessage,
};

const HELP_TOTAL_PAGES: usize = 3;

fn build_help_embed(page: usize) -> CreateEmbed {
    match page {
        0 => CreateEmbed::new()
            .title(format!("ARES Bot Help {}", VERSION))
            .color(Colors::FIRST_BLUE)
            .description(
                "ARES (Analytical Robotics Evaluation System) provides FTC team statistics and match simulations.",
            )
            .field(
                "Core Commands",
                "Use /team to inspect a team and /match to simulate an alliance matchup.",
                false,
            )
            .field(
                "/team <number>",
                "Get detailed information about a specific FTC team, including OPR statistics.",
                false,
            )
            .field(
                "/match <red1> <red2> <blue1> <blue2>",
                "Simulate a match between teams (at least one team required).",
                false,
            )
            .footer(serenity::all::CreateEmbedFooter::new("Page 1/3")),
        1 => CreateEmbed::new()
            .title(format!("ARES Bot Help {}", VERSION))
            .color(Colors::FIRST_BLUE)
            .description("Favorite teams for your server and manage your quick access list.")
            .field(
                "/favorite add <team>",
                "Add a team to your server's favorites.",
                false,
            )
            .field(
                "/favorite remove <team>",
                "Remove a team from your server's favorites.",
                false,
            )
            .field(
                "/favorite toggle <team>",
                "Toggle a team's favorite status.",
                false,
            )
            .field(
                "/favorite list",
                "List all favorite teams in this server.",
                false,
            )
            .footer(serenity::all::CreateEmbedFooter::new("Page 2/3")),
        _ => CreateEmbed::new()
            .title(format!("ARES Bot Help {}", VERSION))
            .color(Colors::FIRST_BLUE)
            .field(
                "About OPR",
                "OPR (Offensive Power Rating) measures a team's average contribution to their alliance's score. Higher OPR generally indicates stronger performance.",
                false,
            )
            .field("/help", "Show this help message.", false)
            .field(
                "Support",
                format!("For issues or questions, contact the developers: {}", DEVELOPERS),
                false,
            )
            .footer(serenity::all::CreateEmbedFooter::new("Page 3/3")),
    }
}

fn build_help_navigation(page: usize) -> Vec<CreateActionRow> {
    let prev_page = page.saturating_sub(1);
    let next_page = if page + 1 >= HELP_TOTAL_PAGES {
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
            .disabled(page + 1 >= HELP_TOTAL_PAGES),
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

pub async fn handle_component(
    ctx: &Context,
    interaction: &ComponentInteraction,
) -> Result<bool> {
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
