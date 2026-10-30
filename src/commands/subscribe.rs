use crate::bot_state::{Colors, error_embed, success_embed, warning_embed};
use crate::commands::{
    bot_can_post, can_manage_channels, cannot_post_here, needs_manage_channels, not_saved,
    option_str, respond, server_only,
};
use crate::live::RouteChange;
use crate::services::Services;
use crate::store::Placement;
use anyhow::Result;
use model::first::{ApiClient, ApiParams, EventCode, EventSummary, EventsResponse};
use serenity::all::{
    ChannelId, CommandInteraction, CommandOptionType, Context, CreateCommand, CreateCommandOption,
    CreateEmbed, CreateEmbedFooter,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    services: &Services,
) -> Result<()> {
    let Some(guild_id) = interaction.guild_id else {
        return respond::public(ctx, interaction, server_only()).await;
    };

    let Some(raw) = option_str(interaction, "event_code") else {
        let embed = match services.subscriptions.list(guild_id).await {
            Ok(subs) => subscriptions_embed(&subs),
            Err(err) => {
                tracing::error!(%guild_id, error = %err, "Could not list subscriptions");
                let embed = error_embed(
                    "Subscriptions Unavailable",
                    "Couldn't load this server's subscriptions. Please try again in a moment.",
                );
                return respond::ephemeral(ctx, interaction, embed).await;
            }
        };
        return respond::public(ctx, interaction, embed).await;
    };

    let Some(first) = services.first.as_ref() else {
        let embed = error_embed(
            "Not Available",
            "Event subscriptions aren't available right now.",
        );
        return respond::ephemeral(ctx, interaction, embed).await;
    };
    if !can_manage_channels(interaction) {
        return respond::ephemeral(ctx, interaction, needs_manage_channels("subscriptions")).await;
    }
    if !bot_can_post(interaction) {
        return respond::ephemeral(ctx, interaction, cannot_post_here()).await;
    }

    let Ok(code) = raw.parse::<EventCode>() else {
        let embed = error_embed(
            "Invalid Event Code",
            "Event codes are letters and numbers, like USAZTUQ. You'll find it on the event's FIRST page.",
        );
        return respond::ephemeral(ctx, interaction, embed).await;
    };
    respond::defer(ctx, interaction).await?;

    let event = match find_event(first, services.season, &code).await {
        Ok(Some(event)) => event,
        Ok(None) => {
            let embed = warning_embed(
                "Unknown Event",
                &format!("Couldn't find an event with the code **{code}** this season."),
            );
            return respond::edit(ctx, interaction, embed).await;
        }
        Err(err) => {
            tracing::error!(event = %code, error = %err, "Could not look up event");
            let embed = error_embed(
                "Event Lookup Failed",
                "Couldn't look that event up right now. Please try again in a moment.",
            );
            return respond::edit(ctx, interaction, embed).await;
        }
    };
    let channel = interaction.channel_id;
    let placement = match services
        .subscriptions
        .subscribe(guild_id, &code, channel)
        .await
    {
        Ok(placement) => placement,
        Err(err) => {
            tracing::error!(%guild_id, event = %code, error = %err, "Could not save subscription");
            return respond::edit(ctx, interaction, not_saved()).await;
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

    respond::edit(ctx, interaction, embed).await
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

pub fn register() -> CreateCommand {
    CreateCommand::new("subscribe")
        .description("Follow every match result from an event in this channel, or see this server's subscriptions.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "event_code",
                "Event code, like USAZTUQ.",
            )
            .required(false),
        )
}
