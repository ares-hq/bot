use anyhow::Result;
use poise::CreateReply;
use serenity::all::{CreateAttachment, CreateEmbed};

use super::Context;

/// Answers the command, or replaces its "thinking" message once deferred.
pub async fn public(ctx: Context<'_>, embed: CreateEmbed) -> Result<()> {
    ctx.send(CreateReply::default().embed(embed)).await?;
    Ok(())
}

/// Only the person who ran the command sees it, unless the reply was already deferred.
pub async fn ephemeral(ctx: Context<'_>, embed: CreateEmbed) -> Result<()> {
    ctx.send(CreateReply::default().embed(embed).ephemeral(true))
        .await?;
    Ok(())
}

pub async fn with_attachment(
    ctx: Context<'_>,
    embed: CreateEmbed,
    attachment: CreateAttachment,
) -> Result<()> {
    ctx.send(CreateReply::default().embed(embed).attachment(attachment))
        .await?;
    Ok(())
}
