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
            match_str = match.__str__()

            winner = match_str[3]
            if winner == "Red":
                color = State.FIRST_RED
            elif winner == "Blue":
                color = State.FIRST_BLUE
            else:
                color = State.FIRST_GRAY

            embed = discord.Embed(title="Match Scoreboard", color=color, timestamp=datetime.now())
            embed.add_field(name="Categories", value=match_str[0], inline=True)
            embed.add_field(name="Red Alliance", value=match_str[1], inline=True) if "" not in match_str[2].strip("`") else None
            embed.add_field(name="Blue Alliance", value=match_str[2], inline=True) if "" not in match_str[2].strip("`") else None
            embed.add_field(name="Match Winner", value=match_str[3], inline=False) if ["Red", "Blue", "Tie"] in match_str[3] else None

        except Exception as e:
            if self.bot.debug_mode:
                print(e)
            await interaction.response.send_message(embed=State.ERROR(), ephemeral=True)
            return

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(cmdMatch(bot))