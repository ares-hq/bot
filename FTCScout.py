import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from Discord.commands import Commands
import Discord.utils as utils

load_dotenv()
class FTCScout(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.debug_mode = False
        self.debug_channel_id = None
        self.favorite_teams = {}
        self.commands = Commands(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced successfully!")

    async def on_ready(self):
        print(f"{self.user.name} ({self.user.id}) is live!")
        await self.change_presence(activity=discord.Game("Into the Deep 🌊"))

    async def on_message(self, message: discord.Message):
        if self.debug_mode and message.channel.id == self.debug_channel_id:
            print(f"Debug: {message.author}: {message.content}")

    def set_debug_mode(self, enabled: bool, channel_id: int = None):
        self.debug_mode = enabled
        self.debug_channel_id = channel_id
        print(f"Debug mode {'enabled' if enabled else 'disabled'}")
        if channel_id:
            print(f"Debug channel ID set to {channel_id}")

    def run_bot(self):
        self.commands.setup_commands()
        self.run(os.getenv('API_KEY'))

if __name__ == '__main__':
    bot = FTCScout()
    bot.set_debug_mode(True, 1214734647695646754)
    bot.run_bot()