use anyhow::{Context as _, Result};
use futures::future::join_all;
use model::first::{EventCode, MatchInfo};
use model::prelude::{Match as Scored, Team, Winner};
use serenity::all::{
    ChannelId, CreateAttachment, CreateEmbed, CreateEmbedFooter, CreateMessage, Http, HttpError,
};
use std::collections::BTreeSet;

use super::Shared;
use crate::alliance::Alliance;
use crate::bot_state::Colors;
use crate::image_generator::ImageGenerator;

const FILE_NAME: &str = "match.png";

pub struct Card {
    embed: CreateEmbed,
    png: Vec<u8>,
}

impl Card {
    pub async fn render(
        shared: &Shared,
        m: &MatchInfo,
        rescored: bool,
        event: &str,
        code: &EventCode,
    ) -> Result<Self> {
        let actual = m.result();
        let numbers: Vec<u32> = actual
            .alliances()
            .into_iter()
            .flat_map(|a| a.present_teams())
            .collect();
        let known = shared.teams.teams(&numbers).await.unwrap_or_else(|err| {
            tracing::warn!(event = %code, error = %err, "Could not read teams for a match card");
            Vec::new()
        });
        let lookup = |n: u32| {
            (n != 0).then(|| {
                known
                    .iter()
                    .find(|t| t.number == n)
                    .cloned()
                    .unwrap_or_else(|| Team::new(n, String::new()))
            })
        };
        let [red, blue] =
            [actual.red.teams, actual.blue.teams].map(|[a, b]| Alliance::new(lookup(a), lookup(b)));
        let predicted = numbers
            .iter()
            .all(|n| known.iter().any(|t| t.number == *n))
            .then(|| Scored::new((&red).into(), (&blue).into()));

        let title = m.title();
        let png = {
            let (actual, title, footer) = (actual.clone(), title.to_uppercase(), event.to_owned());
            tokio::task::spawn_blocking(move || {
                ImageGenerator::create_result_image(&red, &blue, &actual, &title, &footer)
            })
            .await
            .context("match card renderer panicked")??
        };

        Ok(Self {
            embed: embed(&actual, predicted.as_ref(), &title, rescored, event, code),
            png,
        })
    }

    /// Returns the channels that no longer accept posts.
    pub async fn post(self, http: &Http, channels: &BTreeSet<ChannelId>) -> Vec<ChannelId> {
        let sends = channels.iter().map(|&channel| {
            let message = CreateMessage::new()
                .embed(self.embed.clone())
                .add_file(CreateAttachment::bytes(self.png.clone(), FILE_NAME));
            async move { (channel, channel.send_message(http, message).await) }
        });

        join_all(sends)
            .await
            .into_iter()
            .filter_map(|(channel, sent)| match sent {
                Ok(_) => None,
                Err(err) if is_gone(&err) => Some(channel),
                Err(err) => {
                    tracing::warn!(%channel, error = %err, "Could not post match card");
                    None
                }
            })
            .collect()
    }
}

fn embed(
    actual: &Scored,
    predicted: Option<&Scored>,
    title: &str,
    rescored: bool,
    event: &str,
    code: &EventCode,
) -> CreateEmbed {
    let (red, blue) = actual.totals();
    let (verdict, color) = match actual.winner() {
        Some(Winner::Red) => ("Red Alliance Wins!", Colors::CHALLENGE_RED),
        Some(Winner::Blue) => ("Blue Alliance Wins!", Colors::FIRST_BLUE),
        None => ("Tie Match!", Colors::WHITE),
    };

    let embed = CreateEmbed::new()
        .title(if rescored {
            format!("{event} · {title} · Score updated")
        } else {
            format!("{event} · {title}")
        })
        .description(format!("**{verdict}**  {red:.0} – {blue:.0}"))
        .color(color)
        .image(format!("attachment://{FILE_NAME}"))
        .footer(CreateEmbedFooter::new(format!("Event code {code}")));
    match predicted.map(Scored::totals) {
        Some((red, blue)) => embed.field("ARES prediction", format!("{red:.0} – {blue:.0}"), true),
        None => embed,
    }
}

fn is_gone(err: &serenity::Error) -> bool {
    matches!(
        err,
        serenity::Error::Http(HttpError::UnsuccessfulRequest(resp))
            if matches!(resp.status_code.as_u16(), 403 | 404)
    )
}
