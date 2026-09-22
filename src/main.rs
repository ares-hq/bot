mod alliance;
mod bot_state;
mod commands;
mod config;
mod favorites;
mod image_generator;
mod match_data;
mod team_store;

use anyhow::Result;
use serenity::all::{Client, Context, EventHandler, GatewayIntents, Interaction, Ready};
use std::sync::Arc;
use tracing::{error, info};

use bot_state::error_embed;
use commands::{Command, respond};
use config::Config;
use favorites::FavoritesManager;
use team_store::TeamStore;

struct Handler {
    teams: Arc<TeamStore>,
    favorites: Arc<FavoritesManager>,
    config: Arc<Config>,
}

#[serenity::async_trait]
impl EventHandler for Handler {
    async fn ready(&self, ctx: Context, ready: Ready) {
        info!("{} is connected as {}", bot_state::VERSION, ready.user.name);

        let commands: Vec<_> = Command::ALL.into_iter().map(Command::register).collect();

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

        ctx.set_activity(Some(serenity::all::ActivityData::playing(
            bot_state::PRESENCE,
        )));

        info!("{} Bot is ready!", bot_state::NAME);
    }

    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::Command(command) = &interaction {
            if self.config.debug_mode {
                let channel_u64 = command.channel_id.get();
                let allowed = self.config.dev_channel_ids.contains(&channel_u64);

                if !allowed {
                    let embed = error_embed(
                        "Debug Mode",
                        "Bot is in debug mode. Commands are restricted to specific channels.",
                    );
                    let _ = respond::ephemeral(&ctx, command, embed).await;
                    return;
                }
            }

            let Some(name) = Command::from_name(&command.data.name) else {
                let embed = error_embed("Unknown Command", "This command is not recognized.");
                let _ = respond::ephemeral(&ctx, command, embed).await;
                return;
            };

            if let Err(e) = name.run(&ctx, command, &self.teams, &self.favorites).await {
                error!("Error handling command '{}': {}", command.data.name, e);
            }
            return;
        }

        if let Interaction::Component(component) = &interaction
            && let Err(e) = commands::help::handle_component(&ctx, component).await
        {
            error!("Error handling component interaction: {}", e);
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    info!("Starting {} Bot {}", bot_state::NAME, bot_state::VERSION);

    let config = Config::from_env()?;
    info!("Configuration loaded");

    let teams = TeamStore::new(
        &config.supabase_url,
        config.supabase_key.clone(),
        config.season,
    );
    let favorites = FavoritesManager::new(&config.supabase_url, config.supabase_key.clone());

    info!("Services initialized");

    let intents = GatewayIntents::GUILDS | GatewayIntents::DIRECT_MESSAGES;

    let handler = Handler {
        teams: Arc::new(teams),
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
