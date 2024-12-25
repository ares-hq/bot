import discord
from discord import app_commands
from dotenv import load_dotenv
import os

load_dotenv()

# FIRST Team Avatar Logos
# https://ftc-scoring.firstinspires.org/avatars/composed/2025.css


##########################
# Feature Request (API):
# - Tournament Schedule Given a Event Code
# - Team Schedule Given a Team Number
# - Tournament Mode - Live Scoring
# 
# Feature Request (Local Scouting):
# - Manual Scouting
# -- Sample Cycles (Samples, Specimens)
# -- Robot Speed (Fast, Medium, Slow)
# -- Hang Potential (Level 1,2,3, Park)
# -- Specialized? (Samples, Specimens, Both, None)





class FTCScout(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.debug_mode = False
        self.debug_channel_id = None
        self.favorite_teams = {}

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

    def setup_commands(self):
        self.slash_team()
        self.slash_match()
        self.slash_favorite()

    def slash_team(self):
        @self.tree.command(name="team", description="Displays team information.")
        @app_commands.describe(team_number="Details about the team.")
        async def team(interaction: discord.Interaction, team_number: str = None):
            processed_info = str(await handle_user_messages("team " + team_number)) if team_number else "No data available at this time"
            embed = discord.Embed(
                title=processed_info[0],
                description=processed_info[1:],
                color=discord.Color.from_str('#0066B3')
            )
            embed.set_footer(text="Use /team <team_number> for specific team details.")
            await interaction.response.send_message(embed=embed)

    def slash_match(self):
        @self.tree.command(name="match", description="Displays match details.")
        @app_commands.describe(alliance_1="Alliance 1 team numbers.", alliance_2="Alliance 2 team numbers.")
        async def match(interaction: discord.Interaction, alliance_1: str = None, alliance_2: str = None):
            processed_info = str(await handle_user_messages("match " + alliance_1 + " " + alliance_2)) if alliance_1 or alliance_2 else "No data available at this time"
            embed = discord.Embed(
                title=processed_info[0],
                description=processed_info[1:],
                color=discord.Color.from_str('#ED1C24')
            )
            embed.set_footer(text="Use /match info:<details> for more specifics.")
            await interaction.response.send_message(embed=embed)

    def slash_favorite(self):
        @self.tree.command(name="favorite", description="Marks this as your favorite.")
        @app_commands.describe(team_number="The team to mark as favorite.")
        async def favorite(interaction: discord.Interaction, team_number: str):
            server_id = interaction.guild.id
            self.favorite_teams[server_id] = team_number

            try:
                message = await interaction.original_response()
                await message.add_reaction("⭐")
            except discord.errors.NotFound:
                print("Could not add reaction: Message not found")
            except discord.errors.Forbidden:
                print("Could not add reaction: Missing permissions")

            print(f"Team {team_number} is now marked as the favorite for server {server_id}.")

            try:
                await interaction.guild.me.edit(nick=f"Team {team_number} Bot")
            except discord.errors.Forbidden:
                print("Could not change nickname: Missing permissions")

if __name__ == '__main__':
    bot = FTCScout()
    bot.setup_commands()
    bot.set_debug_mode(True, 1214734647695646754)
    bot.run(os.getenv('API_KEY'))