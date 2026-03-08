use crate::bot_state::{Colors, error_embed, success_embed};
use crate::favorites::FavoritesManager;
use anyhow::Result;
use serenity::all::{
    CommandInteraction, CommandOptionType, Context, CreateCommand, CreateCommandOption,
    CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
};

pub async fn run(
    ctx: &Context,
    interaction: &CommandInteraction,
    favorites: &FavoritesManager,
) -> Result<()> {
    let guild_id = match interaction.guild_id {
        Some(id) => id,
        None => {
            let embed = error_embed("Guild Only", "This command can only be used in a server");
            interaction
                .create_response(
                    &ctx.http,
                    CreateInteractionResponse::Message(
                        CreateInteractionResponseMessage::new().embed(embed),
                    ),
                )
                .await?;
            return Ok(());
        }
    };

    let team_number_raw = interaction
        .data
        .options
        .iter()
        .find(|opt| opt.name == "team_number")
        .and_then(|opt| opt.value.as_str());

    // Python behavior: no team_number means show favorites.
    if team_number_raw.is_none() {
        let favorite_teams = favorites.list_favorites(guild_id);

        let embed = if favorite_teams.is_empty() {
            CreateEmbed::new()
                .title("Favorite Teams")
                .color(Colors::FAVORITE)
                .description("No favorite teams set.")
                .footer(serenity::all::CreateEmbedFooter::new(
                    "Run the command with a team number to add it to favorites.",
                ))
        } else {
            let team_list = favorite_teams
                .iter()
                .map(|num| format!("Team {} ⭐", num))
                .collect::<Vec<_>>()
                .join("\n");

            CreateEmbed::new()
                .title("Favorite Teams")
                .color(Colors::FAVORITE)
                .description(team_list)
                .footer(serenity::all::CreateEmbedFooter::new(
                    "Re-run the command with a team number to remove it from favorites.",
                ))
        };

        interaction
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new().embed(embed),
                ),
            )
            .await?;
        return Ok(());
    }

    let team_number = match team_number_raw.unwrap().parse::<i32>() {
        Ok(v) => v,
        Err(_) => {
            let embed = error_embed("Error", "Team Number must be valid.");
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
            return Ok(());
        }
    };

    let added = favorites.toggle_favorite(guild_id, team_number);
    let embed = if added {
        success_embed(
            "Favorite Added",
            &format!("Team {} added to favorites ⭐", team_number),
        )
    } else {
        success_embed(
            "Favorite Removed",
            &format!("Team {} removed from favorites", team_number),
        )
    };

    interaction
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new().embed(embed),
            ),
        )
        .await?;

    Ok(())
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
