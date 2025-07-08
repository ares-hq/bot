import discord
from discord.ext import commands
from Discord.BotState import State

class DeveloperView(discord.ui.View):
    def __init__(self, bot, embed, developer):
        super().__init__(timeout=60)
        self.bot = bot
        self.embed = embed
        self.developer = developer

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Sent!", ephemeral=True)
        await self.send_message_to_all_servers()
        await self.developer.send("Success! The message has been sent to all servers.")
        await self.delete_dm_messages()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelled!", ephemeral=True)
        await self.developer.send("Action cancelled.")
        await self.delete_dm_messages()

    async def send_message_to_all_servers(self):
        for guild in self.bot.guilds:
            channel = self.find_channel(guild)
            if channel:
                await channel.send(embed=self.embed)

    def find_channel(self, guild):
        # Check for channels in the order specified in State.BOT_CHANNELS
        channels = State().CHANNELS 
        for channel_name in channels:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                return channel

        # Default to the first available channel if no preferred channels are found
        if guild.text_channels:
            return guild.text_channels[0]

    async def delete_dm_messages(self):
        dm_channel = self.developer.dm_channel
        if dm_channel is None:
            dm_channel = await self.developer.create_dm()
        async for message in dm_channel.history(limit=100):
            if message.author == self.bot.user:
                await message.delete()

class cmdDeveloper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.developer_ids = {291420737204649985, 751915057973035058}
        self.prefix = "!devcmd"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is not None:  # Ignore messages from guilds
            return

        if message.author.id not in self.developer_ids:
            return

        if not message.content.startswith(self.prefix):
            return

        command_content = message.content[len(self.prefix):].strip()

        if command_content:
            embed = State.ANNOUNCEMENT(description=command_content)
            view = DeveloperView(self.bot, embed, message.author)
            await message.author.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(cmdDeveloper(bot))