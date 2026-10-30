use model::first::ApiClient;
use serenity::all::ChannelId;
use std::sync::Arc;

use crate::favorites::FavoritesManager;
use crate::live::{LiveHandle, RouteChange};
use crate::subscriptions::Subscriptions;
use crate::team_store::TeamStore;

pub struct Services {
    pub teams: Arc<TeamStore>,
    pub favorites: Arc<FavoritesManager>,
    pub subscriptions: Arc<Subscriptions>,
    /// `None` when FIRST credentials are not configured.
    pub first: Option<ApiClient>,
    pub season: i32,
    pub live: LiveHandle,
    /// `Some` in debug mode: commands answer only in these channels.
    pub debug_channels: Option<Vec<ChannelId>>,
}

impl Services {
    pub fn route(&self, change: RouteChange) {
        self.live.send(change);
    }
}
