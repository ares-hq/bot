use crate::bot_state::{Colors, error_embed, success_embed, warning_embed};
use crate::commands::{
    Context, bot_can_post, can_manage_channels, cannot_post_here, needs_manage_channels, not_saved,
    respond,
};
use crate::live::RouteChange;
use crate::store::Placement;
use anyhow::Result;
use model::first::{ApiClient, ApiParams, EventCode, EventSummary, EventsResponse};
use serenity::all::{ChannelId, CreateEmbed, CreateEmbedFooter};

/// Follow every match result from an event in this channel, or see this server's subscriptions.
#[poise::command(slash_command, guild_only)]
pub async fn subscribe(
    ctx: Context<'_>,
    #[description = "Event code, like USAZTUQ."] event_code: Option<String>,
) -> Result<()> {
    let Some(guild_id) = ctx.guild_id() else {
        return Ok(());
    };
    let services = ctx.data();
    let Some(raw) = event_code else {
        let embed = match services.subscriptions.list(guild_id).await {
            Ok(subs) => subscriptions_embed(&subs),
            Err(err) => {
                tracing::error!(%guild_id, error = %err, "Could not list subscriptions");
                let embed = error_embed(
                    "Subscriptions Unavailable",
                    "Couldn't load this server's subscriptions. Please try again in a moment.",
                );
                return respond::ephemeral(ctx, embed).await;
            }
        };
        return respond::public(ctx, embed).await;
    };

    let Some(first) = services.first.as_ref() else {
        let embed = error_embed(
            "Not Available",
            "Event subscriptions aren't available right now.",
        );
        return respond::ephemeral(ctx, embed).await;
    };
    if !can_manage_channels(ctx) {
        return respond::ephemeral(ctx, needs_manage_channels("subscriptions")).await;
    }
    if !bot_can_post(ctx) {
        return respond::ephemeral(ctx, cannot_post_here()).await;
    }

    let Ok(code) = raw.parse::<EventCode>() else {
        let embed = error_embed(
            "Invalid Event Code",
            "Event codes are letters and numbers, like USAZTUQ. You'll find it on the event's FIRST page.",
        );
        return respond::ephemeral(ctx, embed).await;
    };
    ctx.defer().await?;

    let event = match find_event(first, services.season, &code).await {
        Ok(Some(event)) => event,
        Ok(None) => {
            let embed = warning_embed(
                "Unknown Event",
                &format!("Couldn't find an event with the code **{code}** this season."),
            );
            return respond::public(ctx, embed).await;
        }
        Err(err) => {
            tracing::error!(event = %code, error = %err, "Could not look up event");
            let embed = error_embed(
                "Event Lookup Failed",
                "Couldn't look that event up right now. Please try again in a moment.",
            );
            return respond::public(ctx, embed).await;
        }
    };
    let channel = ctx.channel_id();
    let placement = match services
        .subscriptions
        .subscribe(guild_id, &code, channel)
        .await
    {
        Ok(placement) => placement,
        Err(err) => {
            tracing::error!(%guild_id, event = %code, error = %err, "Could not save subscription");
            return respond::public(ctx, not_saved()).await;
        }
    };

    let name = event.name.clone().unwrap_or_else(|| code.to_string());
    let embed = match placement {
        Placement::Added => success_embed(
            "Subscribed",
            &format!("Match results for **{name}** will post in <#{channel}>."),
        ),
        Placement::Moved => success_embed(
            "Subscription Moved",
            &format!("Match results for **{name}** will now post in <#{channel}>."),
        ),
        Placement::Unchanged => warning_embed(
            "Already Subscribed",
            &format!("**{name}** already posts here. Use /unsubscribe to stop it."),
        ),
    };
    if placement != Placement::Unchanged {
        services.route(RouteChange::Subscribed {
            guild: guild_id,
            channel,
            event,
        });
    }

    respond::public(ctx, embed).await
}

async fn find_event(
    first: &ApiClient,
    season: i32,
    code: &EventCode,
) -> Result<Option<EventSummary>> {
    let params = ApiParams::new(vec![season.to_string(), "events".to_owned()])
        .with_query("eventCode", code.as_str());
    let resp: EventsResponse = first.get(&params).await?;
    Ok(resp.events.into_iter().next())
}

fn subscriptions_embed(subs: &[(EventCode, ChannelId)]) -> CreateEmbed {
    let embed = CreateEmbed::new()
        .title("Event Subscriptions")
        .color(Colors::TECH_ORANGE);

    if subs.is_empty() {
        return embed
            .description("This server isn't following any events.")
            .footer(CreateEmbedFooter::new(
                "Use /subscribe with an event code to follow an event.",
            ));
    }

    let listed = subs
        .iter()
        .map(|(code, channel)| format!("**{code}** → <#{channel}>"))
        .collect::<Vec<_>>()
        .join("\n");

    embed.description(listed).footer(CreateEmbedFooter::new(
        "Use /subscribe in another channel to move an event, or /unsubscribe to stop one.",
    ))
}
