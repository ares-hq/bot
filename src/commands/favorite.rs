use crate::bot_state::{Colors, error_embed, success_embed, warning_embed};
use crate::commands::{
    bot_can_post, can_manage_channels, cannot_post_here, needs_manage_channels, not_saved,
    option_str, respond, server_only,
};
use crate::live::RouteChange;
use crate::services::Services;
use crate::store::Placement;
use anyhow::Result;
use serenity::all::{
    ChannelId, CommandInteraction, CommandOptionType, Context, CreateCommand, CreateCommandOption,
    CreateEmbed, CreateEmbedFooter,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    services: &Services,
) -> Result<()> {
    let Some(guild) = interaction.guild_id else {
        return respond::public(ctx, interaction, server_only()).await;
    };

    let Some(raw) = option_str(interaction, "team_number") else {
        let embed = match services.favorites.list_favorites(guild).await {
            Ok(teams) => favorites_embed(&teams),
            Err(err) => {
                tracing::error!(%guild, error = %err, "Could not list favorites");
                let embed = error_embed(
                    "Favorites Unavailable",
                    "Couldn't load this server's favorites. Please try again in a moment.",
                );
                return respond::ephemeral(ctx, interaction, embed).await;
            }
        };
        return respond::public(ctx, interaction, embed).await;
    };

    let Ok(team) = raw.trim().parse::<u32>() else {
        let embed = error_embed("Invalid Team Number", "Enter a team number, like 14584.");
        return respond::ephemeral(ctx, interaction, embed).await;
    };
    if !can_manage_channels(interaction) {
        return respond::ephemeral(ctx, interaction, needs_manage_channels("favorites")).await;
    }
    if !bot_can_post(interaction) {
        return respond::ephemeral(ctx, interaction, cannot_post_here()).await;
    }

    let channel = interaction.channel_id;
    let placement = match services.favorites.favorite(guild, team, channel).await {
        Ok(placement) => placement,
        Err(err) => {
            tracing::error!(%guild, team, error = %err, "Could not save favorite");
            return respond::ephemeral(ctx, interaction, not_saved()).await;
        }
    };
    if placement != Placement::Unchanged {
        services.route(RouteChange::Favorited {
            guild,
            channel,
            team,
        });
    }

    let embed = match placement {
        Placement::Added => success_embed(
            "Favorite Added",
            &format!("Team {team} added to favorites ⭐\nMatch results will post in <#{channel}>."),
        ),
        Placement::Moved => success_embed(
            "Favorite Moved",
            &format!("Team {team} match results will now post in <#{channel}>."),
        ),
        Placement::Unchanged => warning_embed(
            "Already a Favorite",
            &format!("Team {team} already posts here. Use /unfavorite to remove it."),
        ),
    };
    respond::public(ctx, interaction, embed).await
}

fn favorites_embed(teams: &[(u32, Option<ChannelId>)]) -> CreateEmbed {
    let embed = CreateEmbed::new()
        .title("Favorite Teams")
        .color(Colors::FAVORITE);

    if teams.is_empty() {
        return embed
            .description("No favorite teams set.")
            .footer(CreateEmbedFooter::new(
                "Use /favorite with a team number to add one.",
            ));
    }

    let listed = teams
        .iter()
        .map(|(number, channel)| match channel {
            Some(channel) => format!("Team {number} ⭐ → <#{channel}>"),
            None => format!("Team {number} ⭐"),
        })
        .collect::<Vec<_>>()
        .join("\n");

    embed.description(listed).footer(CreateEmbedFooter::new(
        "Use /favorite in another channel to move a team, or /unfavorite to remove one.",
    ))
}

pub fn register() -> CreateCommand {
    CreateCommand::new("favorite")
        .description(
            "Follow a team's match results in this channel, or see this server's favorites.",
        )
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "team_number",
                "Team number, like 14584.",
            )
            .required(false),
        )
}
