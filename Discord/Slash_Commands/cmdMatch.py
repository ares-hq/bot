import discord
from discord import app_commands
from discord.ext import commands
from Response_Handler import HandleMessageResponse as msg
from datetime import datetime
from Discord.BotState import State

class cmdMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="match", description="Displays match details.")
    @app_commands.describe(red_alliance="Red Alliance team numbers (space-separated).", blue_alliance="Blue Alliance team numbers (space-separated, optional).")
    async def match(self, interaction: discord.Interaction, red_alliance: str, blue_alliance: str = None):
        if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
            return

        red_alliance_teams = [team.strip() for team in red_alliance.split()]
        blue_alliance_teams = [team.strip() for team in blue_alliance.split()] if blue_alliance else []

        if len(red_alliance_teams) != 2 or (blue_alliance and len(blue_alliance_teams) != 2):
            embed = State.WARNING(description="Each alliance must have exactly 2 team numbers separated by a space.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            match = msg.match_message_data(red_alliance_teams, blue_alliance_teams)
            winner = match.winner

            if winner == "Tie" or not blue_alliance_teams:
                color = State.FIRST_GRAY
            elif winner == "Red":
                color = State.FIRST_RED
            elif winner == "Blue":
                color = State.FIRST_BLUE

            embed = discord.Embed(title="Match Scoreboard", color=color, timestamp=datetime.now())
            embed.add_field(name="Categories", value=f"```{'\n'.join(match.matchCategories)}```", inline=True)
            embed.add_field(name="Red Alliance", value=f"```\n{'\n'.join(match.redAlliance.scoreboard)}```", inline=True)
            
            if blue_alliance_teams: # If blue alliance is provided, make full match embed
                embed.add_field(name="Blue Alliance", value=f"```\n{'\n'.join(match.blueAlliance.scoreboard)}```", inline=True)
                if winner != "Tie":
                    winner_team_1 = match.blueAlliance.teamNames[0][:44] + '...' if len(match.blueAlliance.teamNames[0]) > 44 else match.blueAlliance.teamNames[0]
                    winner_team_2 = match.blueAlliance.teamNames[1][:44] + '...' if len(match.blueAlliance.teamNames[1]) > 44 else match.blueAlliance.teamNames[1]
                    embed.add_field(name="Match Winner", value=f"```\n{match.winner} Alliance\nTeam 1: {winner_team_1}\nTeam 2: {winner_team_2}```", inline=False)
                else:
                    embed.add_field(name="Match Winner", value=f"```\n{match.winner}```", inline=False)

        except Exception as e:
            if self.bot.debug_mode:
                print(e)
            await interaction.response.send_message(embed=State.ERROR(), ephemeral=True)
            return

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(cmdMatch(bot))