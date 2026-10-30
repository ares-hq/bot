use crate::bot_state::{error_embed, success_embed, warning_embed};
use crate::commands::{
    can_manage_channels, needs_manage_channels, not_saved, option_str, respond, server_only,
    suggest,
};
use crate::live::RouteChange;
use crate::services::Services;
use anyhow::Result;
use model::first::EventCode;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateCommand, CreateCommandOption,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    services: &Services,
) -> Result<()> {
    let Some(guild) = interaction.guild_id else {
        return respond::public(ctx, interaction, server_only()).await;
    };
    let Some(Ok(code)) = option_str(interaction, "event_code").map(str::parse::<EventCode>) else {
        let embed = error_embed(
            "Invalid Event Code",
            "Event codes are letters and numbers, like USAZTUQ.",
        );
        return respond::ephemeral(ctx, interaction, embed).await;
    };
    if !can_manage_channels(interaction) {
        return respond::ephemeral(ctx, interaction, needs_manage_channels("subscriptions")).await;
    }

    let embed = match services.subscriptions.unsubscribe(guild, &code).await {
        Ok(true) => {
            let embed = success_embed(
                "Unsubscribed",
                &format!("No longer posting match results for **{code}**."),
            );
            services.route(RouteChange::Unsubscribed { guild, code });
            embed
        }
        Ok(false) => warning_embed(
            "Not Subscribed",
            &format!("This server isn't following **{code}**."),
        ),
        Err(err) => {
            tracing::error!(%guild, event = %code, error = %err, "Could not unsubscribe");
            return respond::ephemeral(ctx, interaction, not_saved()).await;
        }
    };
    respond::public(ctx, interaction, embed).await
}

/// Suggests the events this server follows.
pub async fn autocomplete(
    ctx: &Context,
    interaction: &CommandInteraction,
    services: &Services,
) -> Result<()> {
    let Some(guild) = interaction.guild_id else {
        return Ok(());
    };
    let choices = services
        .subscriptions
        .list(guild)
        .await?
        .into_iter()
        .map(|(code, _)| (code.to_string(), code.into_string()));
    suggest(ctx, interaction, choices).await
}

pub fn register() -> CreateCommand {
    CreateCommand::new("unsubscribe")
        .description("Stop following an event's match results.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "event_code",
                "One of the events this server follows.",
            )
            .required(true)
            .set_autocomplete(true),
        )
}
