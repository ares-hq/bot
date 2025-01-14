import discord
from discord import app_commands
from discord.ext import commands
from Response_Handler import HandleMessageResponse as msg
from datetime import datetime
from Discord.BotState import State
from Discord.Slash_Commands.MatchImageCreator import ImageCreator
import os

class cmdMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="match", description="Displays match details.")
    @app_commands.describe(red_alliance="Red Alliance team numbers (space-separated).", blue_alliance="Blue Alliance team numbers (space-separated, optional).")
    async def match(self, interaction: discord.Interaction, red_alliance: str, blue_alliance: str = None):
        if self.bot.debug_mode and interaction.channel_id not in self.bot.debug_channel_ids:
            return

        try:
            red_alliance_teams = [team.strip() for team in red_alliance.split()]
            blue_alliance_teams = [team.strip() for team in blue_alliance.split()] if blue_alliance else []

            if len(red_alliance_teams) != 2 or (blue_alliance and len(blue_alliance_teams) != 2):
                embed = State.WARNING(description="Each alliance must have exactly 2 team numbers separated by a space.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            match = msg.match_message_data(red_alliance_teams, blue_alliance_teams)
            winner = match.winner if blue_alliance_teams else None

            image_name = "match_scoreboard.png"
            
            if match.blueAlliance.teamNames[0] == "":
                image = ImageCreator.createAllianceImage(
                    team_names=match.redAlliance.teamNames,
                    team_scores=match.redAlliance
                )
            else:
                image = ImageCreator.createMatchImage(
                    red_team_names=match.redAlliance.teamNames,
                    blue_team_names=match.blueAlliance.teamNames,
                    red_team=match.redAlliance.scoreboard,
                    blue_team=match.blueAlliance.scoreboard,
                )
            
            image.save(image_name, format="PNG")

            color = State.WHITE if winner == "Tie" or not blue_alliance_teams else (
                State.CHALLENGE_RED if winner == "Red" else State.FIRST_BLUE
            )

            embed = discord.Embed(title="Match Scoreboard", color=color, timestamp=datetime.now())
            embed.set_image(url=f"attachment://{image_name}")

            file = discord.File(image_name, filename=image_name)
            await interaction.response.send_message(embed=embed, file=file)
            
            os.remove(image_name)

        except Exception as e:
            if self.bot.debug_mode:
                print(f"Error: {e}")
            embed = State.ERROR(title="Error", description="An error occurred while processing the match data.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(cmdMatch(bot))