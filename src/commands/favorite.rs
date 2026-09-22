use crate::bot_state::{Colors, error_embed, success_embed};
use crate::commands::{option_str, respond};
use crate::favorites::FavoritesManager;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateCommand, CreateCommandOption,
    CreateEmbed, CreateEmbedFooter,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    favorites: &FavoritesManager,
) -> Result<()> {
    let Some(guild_id) = interaction.guild_id else {
        let embed = error_embed("Guild Only", "This command can only be used in a server.");
        return respond::public(ctx, interaction, embed).await;
    };

    let Some(raw) = option_str(interaction, "team_number") else {
        let embed = match favorites.list_favorites(guild_id).await {
            Ok(teams) => favorites_embed(&teams),
            Err(err) => {
                tracing::error!(%guild_id, error = %err, "Could not list favorites");
                let embed = error_embed(
                    "Favorites Unavailable",
                    "Could not read this server's favorites. Try again shortly.",
                );
                return respond::ephemeral(ctx, interaction, embed).await;
            }
        };
        return respond::public(ctx, interaction, embed).await;
    };

    let Ok(team_number) = raw.parse::<u32>() else {
        let embed = error_embed("Error", "Team number must be numerical.");
        return respond::ephemeral(ctx, interaction, embed).await;
    };

    let embed = match favorites.toggle_favorite(guild_id, team_number).await {
        Ok(true) => success_embed(
            "Favorite Added",
            &format!("Team {team_number} added to favorites ⭐"),
        ),
        Ok(false) => success_embed(
            "Favorite Removed",
            &format!("Team {team_number} removed from favorites"),
        ),
        Err(err) => {
            tracing::error!(%guild_id, team_number, error = %err, "Could not save favorite");
            let embed = error_embed(
                "Favorite Not Saved",
                "Could not reach the favorites store. Nothing was changed.",
            );
            return respond::ephemeral(ctx, interaction, embed).await;
        }
    };

    respond::public(ctx, interaction, embed).await
}

fn favorites_embed(teams: &[u32]) -> CreateEmbed {
    let embed = CreateEmbed::new()
        .title("Favorite Teams")
        .color(Colors::FAVORITE);

    if teams.is_empty() {
        return embed
            .description("No favorite teams set.")
            .footer(CreateEmbedFooter::new(
                "Run the command with a team number to add it to favorites.",
            ));
    }

    let listed = teams
        .iter()
        .map(|number| format!("Team {number} ⭐"))
        .collect::<Vec<_>>()
        .join("\n");

    embed.description(listed).footer(CreateEmbedFooter::new(
        "Re-run the command with a team number to remove it from favorites.",
    ))
}

pub fn register() -> CreateCommand {
    CreateCommand::new("favorite")
        .description("Marks this as your favorite or shows favorite teams.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "team_number",
                "The team to mark as favorite.",
            )
            .required(false),
        )
}
