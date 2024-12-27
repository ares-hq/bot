import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from Discord.commands import Commands

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
        if self.debug_mode:
            # Use a separate command tree for the development environment
            self.tree.copy_global_to(guild=discord.Object(id=os.getenv("DEV_SERVER_ID")))
            await self.tree.sync(guild=discord.Object(id=os.getenv("DEV_SERVER_ID")))
        else:
            # Use the global command tree for the production environment
            await self.tree.sync()
        self._load_favorite_teams()

    async def on_ready(self):
        print(f"{self.user.name} ({self.user.id}) is live!")
        await self.change_presence(activity=discord.Game("Into the Deep 🌊"))

    async def on_message(self, message: discord.Message):
        if self.debug_mode and message.channel.id == self.debug_channel_id:
            print(f"Debug: {message.author}: {message.content}")

    def set_debug_mode(self, enabled: bool, channel_id: int = None):
        self.debug_mode = enabled
        self.debug_channel_id = channel_id

    def _load_favorite_teams(self):
        self.favorite_teams = {}
        for guild in self.guilds:
            for member in guild.members:
                if member.bot and member.nick:
                    # print(f"Checking bot nickname: {member.nick}")
                    if member.nick.startswith("Team ") and member.nick.endswith(" Bot"):
                        try:
                            team_number = int(member.nick.split(" ")[1])
                            self.favorite_teams[guild.id] = team_number
                            print(f"Added team {team_number} for guild {guild.id}")
                        except ValueError:
                            continue
        print("Favorite teams loaded.")

    def run_bot(self):
        self.key = os.getenv('DISCORD_TOKEN')
        if not self.key:
            raise EnvironmentError("Environment variable DISCORD_TOKEN is required.")
        self.run(self.key)

        

if __name__ == '__main__':
    bot = FTCScout()
    bot.set_debug_mode(True, int(os.getenv("DEV_CHANNEL_ID")))
    bot.run_bot()