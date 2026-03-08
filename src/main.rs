mod alliance;
mod bot_state;
mod commands;
mod config;
mod favorites;
mod image_generator;
mod match_data;
mod supabase_handler;

use anyhow::Result;
use serenity::all::{
    Client, Context, CreateCommand, CreateInteractionResponse, CreateInteractionResponseMessage,
    EventHandler, GatewayIntents, Interaction, Ready,
};
use std::sync::Arc;
use tracing::{error, info};

use bot_state::error_embed;
use config::Config;
use favorites::FavoritesManager;
use supabase_handler::SupabaseHandler;

struct Handler {
    supabase: Arc<SupabaseHandler>,
    favorites: Arc<FavoritesManager>,
    config: Arc<Config>,
}

#[serenity::async_trait]
impl EventHandler for Handler {
    async fn ready(&self, ctx: Context, ready: Ready) {
        info!("{} is connected as {}", bot_state::VERSION, ready.user.name);

        // Register slash commands
        let commands = vec![
            commands::team::register(),
            commands::match_cmd::register(),
            commands::favorite::register(),
            commands::help::register(),
        ];

        // Register commands either globally or to dev server
        if self.config.debug_mode {
            if let Some(dev_server) = self.config.dev_server_id {
                info!("Registering commands to development server: {}", dev_server);
                if let Err(e) = serenity::all::GuildId::new(dev_server)
                    .set_commands(&ctx.http, commands)
                    .await
                {
                    error!("Failed to register guild commands: {}", e);
                }
            }
        } else {
            info!("Registering commands globally");
            if let Err(e) = serenity::all::Command::set_global_commands(&ctx.http, commands).await {
                error!("Failed to register global commands: {}", e);
            }
        }

        // Set activity
        ctx.set_activity(Some(serenity::all::ActivityData::playing(
            bot_state::PRESENCE,
        )));

        info!("{} Bot is ready!", bot_state::NAME);
    }

    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::Command(command) = interaction {
            // Check debug mode channel filtering
            if self.config.debug_mode {
                let channel_u64 = command.channel_id.get();
                let allowed = self.config.dev_channel_ids.contains(&channel_u64);

                if !allowed {
                    let embed = error_embed(
                        "Debug Mode",
                        "Bot is in debug mode. Commands are restricted to specific channels.",
                    );
                    let _ = command
                        .create_response(
                            &ctx.http,
                            CreateInteractionResponse::Message(
                                CreateInteractionResponseMessage::new()
                                    .embed(embed)
                                    .ephemeral(true),
                            ),
                        )
                        .await;
                    return;
                }
            }

            let result = match command.data.name.as_str() {
                "team" => {
                    commands::team::run(&ctx, &command, &self.supabase, &self.favorites).await
                }
                "match" => commands::match_cmd::run(&ctx, &command, &self.supabase).await,
                "favorite" => commands::favorite::run(&ctx, &command, &self.favorites).await,
                "help" => commands::help::run(&ctx, &command).await,
                _ => {
                    let embed = error_embed("Unknown Command", "This command is not recognized.");
                    let _ = command
                        .create_response(
                            &ctx.http,
                            CreateInteractionResponse::Message(
                                CreateInteractionResponseMessage::new()
                                    .embed(embed)
                                    .ephemeral(true),
                            ),
                        )
                        .await;
                    Ok(())
                }
            };

            if let Err(e) = result {
                error!("Error handling command '{}': {}", command.data.name, e);
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    info!("Starting {} Bot {}", bot_state::NAME, bot_state::VERSION);

    // Load configuration
    let config = Config::from_env()?;
    info!("Configuration loaded");

    // Initialize services
    let supabase = SupabaseHandler::new(config.supabase_url.clone(), config.supabase_key.clone());
    let favorites = FavoritesManager::new();

    info!("Services initialized");

    // Set up Discord client
    let intents = GatewayIntents::GUILDS | GatewayIntents::DIRECT_MESSAGES;

    let handler = Handler {
        supabase: Arc::new(supabase),
        favorites: Arc::new(favorites),
        config: Arc::new(config.clone()),
    };

    let mut client = Client::builder(&config.discord_token, intents)
        .event_handler(handler)
        .await?;

    info!("Starting Discord client...");
    client.start().await?;

    Ok(())
}
