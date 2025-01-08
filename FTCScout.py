import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os
from Discord.commands import Commands
from Discord import State

load_dotenv()

class FTCScout(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)
        self.debug_mode = False
        self.debug_channel_id = None
        self.favorite_teams = {}
        self.slash_commands = Commands(self)

    async def setup_hook(self):
        await self.slash_commands.setup()
        if self.debug_mode:
            # Use a separate command tree for the development environment
            dev_guild = discord.Object(id=os.getenv("DEV_SERVER_ID"))
            self.tree.copy_global_to(guild=dev_guild)
            self.set_debug_mode(True, int(os.getenv("DEV_CHANNEL_ID")))
            print("Development Mode: Active")
            await self.tree.sync(guild=dev_guild)
        else:
            # Use the global command tree for the production environment
            await self.tree.sync()

    async def on_ready(self):
        print(f"{self.user.name} ({self.user.id}) is now live in {len(self.guilds)} servers!")
        await self.change_presence(activity=discord.Game("Into the Deep 🌊"))
        # for guild in self.guilds:
        #     await guild.me.edit(nick=None) # Reset bot nickname

    async def on_message(self, message: discord.Message):
        if self.debug_mode and message.channel.id == self.debug_channel_id:
            print(f"Debug: {message.author}: {message.content}")

    def set_debug_mode(self, enabled: bool, channel_id: int = None):
        self.debug_mode = enabled
        self.debug_channel_id = channel_id

    # def _load_favorite_teams(self):
    #     pass
    #     print(f"Favorite teams loaded ({len(self.favorite_teams)})")

    def run_bot(self):
        self.key = os.getenv('DISCORD_TOKEN')
        if not self.key:
            raise EnvironmentError("Environment variable DISCORD_TOKEN is required.")
        self.run(self.key)

if __name__ == '__main__':
    bot = FTCScout()
    bot.set_debug_mode(True, int(os.getenv("DEV_CHANNEL_ID")))
    bot.run_bot()