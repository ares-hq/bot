mod alliance;
mod bot_state;
mod commands;
mod config;
mod favorites;
mod image_generator;
mod live;
mod match_data;
mod services;
mod store;
mod subscriptions;
mod team_store;

use anyhow::Result;
use serenity::all::{
    ActivityData, ClientBuilder, Command, FullEvent, GatewayIntents, Interaction,
};
use std::sync::Arc;
use tracing::{error, info, warn};
use tracing_subscriber::EnvFilter;

use commands::Error;
use config::Config;
use favorites::FavoritesManager;
use live::{Live, LiveHandle};
use model::first::{self, ApiClient};
use model::prelude::Supabase;
use services::Services;
use subscriptions::Subscriptions;
use team_store::TeamStore;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env().add_directive(tracing::Level::INFO.into()))
        .init();

    info!("Starting {} Bot {}", bot_state::NAME, bot_state::VERSION);

    let config = Config::from_env()?;
    info!("Configuration loaded");

    let season = config.year();
    let first = match &config.first_credentials {
        Some((user, pass)) => Some(ApiClient::new(first::BASE_URL, user.clone(), pass.clone())?),
        None => {
            warn!("FIRST_USERNAME/FIRST_PASS unset; live match cards disabled");
            None
        }
    };
    let db = Supabase::new(&config.supabase_url, config.supabase_key.clone());
    let (live, inbox) = LiveHandle::channel();
    let services = Arc::new(Services {
        teams: Arc::new(TeamStore::new(db.clone(), season)),
        favorites: Arc::new(FavoritesManager::new(db.clone())),
        subscriptions: Arc::new(Subscriptions::new(db.clone(), season)),
        first: first.clone(),
        season,
        live,
        debug_channels: config.debug_mode.then(|| config.dev_channel_ids.clone()),
    });

    info!("Services initialized");

    let framework = poise::Framework::builder()
        .options(poise::FrameworkOptions {
            commands: commands::all(),
            on_error: |error| Box::pin(commands::on_error(error)),
            command_check: Some(|ctx| Box::pin(commands::allowed_here(ctx))),
            event_handler: |framework, event| Box::pin(on_event(framework, event)),
            ..Default::default()
        })
        .setup({
            let services = services.clone();
            let (debug_mode, dev_server) = (config.debug_mode, config.dev_server_id);
            move |ctx, ready, framework| {
                Box::pin(async move {
                    info!("{} is connected as {}", bot_state::VERSION, ready.user.name);

                    let commands =
                        poise::builtins::create_application_commands(&framework.options().commands);
                    let registered = match (debug_mode, dev_server) {
                        (false, _) => {
                            info!("Registering commands globally");
                            Command::set_global_commands(ctx, commands).await.map(drop)
                        }
                        (true, Some(guild)) => {
                            info!("Registering commands to development server: {guild}");
                            guild.set_commands(ctx, commands).await.map(drop)
                        }
                        (true, None) => Ok(()),
                    };
                    if let Err(e) = registered {
                        error!("Failed to register commands: {e}");
                    }

                    ctx.set_activity(Some(ActivityData::playing(bot_state::PRESENCE)));
                    info!("{} Bot is ready!", bot_state::NAME);
                    Ok(services)
                })
            }
        })
        .build();

    let intents = GatewayIntents::GUILDS | GatewayIntents::DIRECT_MESSAGES;
    let mut client = ClientBuilder::new(&config.discord_token, intents)
        .framework(framework)
        .await?;

    if let Some(first) = first {
        let live = Live::new(&services, first, db, client.http.clone(), inbox);
        tokio::spawn(live.run());
        info!("Live match cards enabled for season {season}");
    }

    info!("Starting Discord client...");
    client.start().await?;
    Ok(())
}

async fn on_event(
    framework: poise::FrameworkContext<'_, Arc<Services>, Error>,
    event: &FullEvent,
) -> Result<()> {
    if let FullEvent::InteractionCreate {
        interaction: Interaction::Component(component),
    } = event
    {
        commands::help::handle_component(framework.serenity_context, component).await?;
    }
    Ok(())
}
