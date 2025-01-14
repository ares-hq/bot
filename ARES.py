import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from Discord.commands import Commands
from Discord import State

load_dotenv()

class ARES(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)
        self.favorite_teams = {}
        self.slash_commands = Commands(self)
        self.debug_mode = False
        self.debug_channel_ids = []

    async def setup_hook(self):
        await self.slash_commands.setup()
        if self.debug_mode:
            dev_guild = discord.Object(id=os.getenv("DEV_SERVER_ID1"))
            self.tree.copy_global_to(guild=dev_guild)
            print(f"Development Mode: Active in channels: {", ".join(map(str, self.debug_channel_ids))}")
            await self.tree.sync(guild=dev_guild)
        else:
            print("Development Mode: Inactive")
            await self.tree.sync()

    async def on_ready(self):
        print(f"{self.user.name} ({self.user.id}) is now live in {len(self.guilds)} servers!")
        await self.change_presence(activity=discord.Game("Into the Deep 🌊"))

    async def on_message(self, message: discord.Message):
        if self.debug_mode and message.channel.id not in self.debug_channel_ids:
            return  
        print(f"Message from {message.author}: {message.content}")
        await self.process_commands(message)

    def run_bot(self, debug_mode: bool = False, debug_channel_ids: int = [int(os.getenv("DEV_CHANNEL_ID1"))]):
        self.debug_mode = debug_mode
        self.debug_channel_ids = debug_channel_ids

        self.key = os.getenv('DISCORD_TOKEN')
        if not self.key:
            raise EnvironmentError("Environment variable DISCORD_TOKEN is required.")
        
        self.run(self.key)

if __name__ == '__main__':
    bot = ARES()
    bot.run_bot(debug_mode=True, dev_channel_ids=[int(os.getenv("DEV_CHANNEL_ID1")), int(os.getenv("DEV_CHANNEL_ID2"))])