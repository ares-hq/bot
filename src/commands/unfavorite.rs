use crate::bot_state::{success_embed, warning_embed};
use crate::commands::{Context, matching, not_saved, respond};
use crate::live::RouteChange;
use anyhow::Result;
use serenity::all::CreateAutocompleteResponse;

/// Stop following a team's match results.
#[poise::command(
    slash_command,
    guild_only,
    default_member_permissions = "MANAGE_CHANNELS"
)]
pub async fn unfavorite(
    ctx: Context<'_>,
    #[description = "One of this server's favorite teams."]
    #[min = 1]
    #[autocomplete = "suggest_favorites"]
    team_number: u32,
) -> Result<()> {
    let Some(guild) = ctx.guild_id() else {
        return Ok(());
    };
    let services = ctx.data();
    let team = team_number;

    let embed = match services.favorites.unfavorite(guild, team).await {
        Ok(true) => {
            services.route(RouteChange::Unfavorited { guild, team });
            success_embed(
                "Favorite Removed",
                &format!("Team {team} removed from favorites."),
            )
        }
        Ok(false) => warning_embed(
            "Not a Favorite",
            &format!("Team {team} isn't one of this server's favorites."),
        ),
        Err(err) => {
            tracing::error!(%guild, team, error = %err, "Could not remove favorite");
            return respond::ephemeral(ctx, not_saved()).await;
        }
    };
    respond::public(ctx, embed).await
}

/// This server's favorites, named when the team is known.
async fn suggest_favorites(ctx: Context<'_>, typed: &str) -> CreateAutocompleteResponse {
    let response = CreateAutocompleteResponse::new();
    let Some(guild) = ctx.guild_id() else {
        return response;
    };
    let services = ctx.data();
    let numbers: Vec<u32> = match services.favorites.list_favorites(guild).await {
        Ok(favorites) => favorites.into_iter().map(|(number, _)| number).collect(),
        Err(err) => {
            tracing::warn!(%guild, error = %err, "Could not suggest favorites");
            return response;
        }
    };
    let known = services.teams.teams(&numbers).await.unwrap_or_default();

    let choices = numbers.into_iter().map(|number| {
        let label = match known.iter().find(|t| t.number == number) {
            Some(team) if !team.name.is_empty() => format!("{number} · {}", team.name),
            _ => format!("Team {number}"),
        };
        (label, number)
    });
    matching(typed, choices).fold(response, |r, (label, number)| {
        r.add_int_choice(label, number.into())
    })
}
