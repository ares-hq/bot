use anyhow::Result;
use serenity::all::{
    CommandInteraction, Context, CreateAttachment, CreateEmbed, CreateInteractionResponse,
    CreateInteractionResponseMessage, EditInteractionResponse,
};

pub async fn ephemeral(
    ctx: &Context,
    interaction: &CommandInteraction,
    embed: CreateEmbed,
) -> Result<()> {
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
    Ok(())
}

pub async fn public(
    ctx: &Context,
    interaction: &CommandInteraction,
    embed: CreateEmbed,
) -> Result<()> {
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

pub async fn defer(ctx: &Context, interaction: &CommandInteraction) -> Result<()> {
    interaction
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Defer(CreateInteractionResponseMessage::new()),
        )
        .await?;
    Ok(())
}

pub async fn edit(
    ctx: &Context,
    interaction: &CommandInteraction,
    embed: CreateEmbed,
) -> Result<()> {
    interaction
        .edit_response(&ctx.http, EditInteractionResponse::new().embed(embed))
        .await?;
    Ok(())
}

pub async fn edit_with_attachment(
    ctx: &Context,
    interaction: &CommandInteraction,
    embed: CreateEmbed,
    attachment: CreateAttachment,
) -> Result<()> {
    interaction
        .edit_response(
            &ctx.http,
            EditInteractionResponse::new()
                .embed(embed)
                .new_attachment(attachment),
        )
        .await?;
    Ok(())
}
