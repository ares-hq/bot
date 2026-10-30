use crate::bot_state::{error_embed, success_embed, warning_embed};
use crate::commands::{Context, matching, not_saved, respond};
use crate::live::RouteChange;
use anyhow::Result;
use model::first::EventCode;
use serenity::all::CreateAutocompleteResponse;

/// Stop following an event's match results.
#[poise::command(
    slash_command,
    guild_only,
    default_member_permissions = "MANAGE_CHANNELS"
)]
pub async fn unsubscribe(
    ctx: Context<'_>,
    #[description = "One of the events this server follows."]
    #[autocomplete = "suggest_events"]
    event_code: String,
) -> Result<()> {
    let Some(guild) = ctx.guild_id() else {
        return Ok(());
    };
    let Ok(code) = event_code.parse::<EventCode>() else {
        let embed = error_embed(
            "Invalid Event Code",
            "Event codes are letters and numbers, like USAZTUQ.",
        );
        return respond::ephemeral(ctx, embed).await;
    };
    let services = ctx.data();

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
            return respond::ephemeral(ctx, not_saved()).await;
        }
    };
    respond::public(ctx, embed).await
}

/// The events this server follows.
async fn suggest_events(ctx: Context<'_>, typed: &str) -> CreateAutocompleteResponse {
    let response = CreateAutocompleteResponse::new();
    let Some(guild) = ctx.guild_id() else {
        return response;
    };
    let subscriptions = match ctx.data().subscriptions.list(guild).await {
        Ok(subscriptions) => subscriptions,
        Err(err) => {
            tracing::warn!(%guild, error = %err, "Could not suggest events");
            return response;
        }
    };
    let choices = subscriptions
        .into_iter()
        .map(|(code, _)| (code.to_string(), code.into_string()));
    matching(typed, choices).fold(response, |r, (label, code)| {
        r.add_string_choice(label, code)
    })
}
