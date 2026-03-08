use crate::bot_state::{Colors, DEVELOPERS, VERSION};
use anyhow::Result;
use serenity::all::{
    CommandInteraction, Context, CreateCommand, CreateEmbed, CreateInteractionResponse,
    CreateInteractionResponseMessage,
};

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> Result<()> {
    let embed = CreateEmbed::new()
        .title(format!("ARES Bot Help {}", VERSION))
        .color(Colors::FIRST_BLUE)
        .description("ARES (Analytical Robotics Evaluation System) provides FTC team statistics and match simulations.")
        .field(
            "/team <number>",
            "Get detailed information about a specific FTC team, including OPR statistics",
            false,
        )
        .field(
            "/match <red1> <red2> <blue1> <blue2>",
            "Simulate a match between teams (at least one team required)",
            false,
        )
        .field(
            "/favorite add <team>",
            "Add a team to your server's favorites",
            false,
        )
        .field(
            "/favorite remove <team>",
            "Remove a team from your server's favorites",
            false,
        )
        .field(
            "/favorite toggle <team>",
            "Toggle a team's favorite status",
            false,
        )
        .field(
            "/favorite list",
            "List all favorite teams in this server",
            false,
        )
        .field(
            "/help",
            "Show this help message",
            false,
        )
        .field(
            "About OPR",
            "OPR (Offensive Power Rating) measures a team's average contribution to their alliance's score. Higher OPR generally indicates stronger performance.",
            false,
        )
        .field(
            "Support",
            format!("For issues or questions, contact the developers: {}", DEVELOPERS),
            false,
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

    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("help").description("Show help information about ARES bot commands")
}
