import discord
from discord import app_commands
from discord.ext import commands
from Response_Handler import HandleMessageResponse as msg
from datetime import datetime
from Discord.BotState import State
import os
from html2image import Html2Image
from jinja2 import Template

class cmdMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="match", description="Displays match details.")
    @app_commands.describe(red_alliance="Red Alliance team numbers (space-separated).", blue_alliance="Blue Alliance team numbers (space-separated, optional).")
    async def match(self, interaction: discord.Interaction, red_alliance: str, blue_alliance: str = None):
        if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
            return

        # Defer response to allow processing time
        await interaction.response.defer()

        red_alliance_teams = [team.strip() for team in red_alliance.split()]
        blue_alliance_teams = [team.strip() for team in blue_alliance.split()] if blue_alliance else []

        if len(red_alliance_teams) != 2 or (blue_alliance and len(blue_alliance_teams) != 2):
            embed = State.WARNING(description="Each alliance must have exactly 2 team numbers separated by a space.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        try:
            match = msg.match_message_data(red_alliance_teams, blue_alliance_teams)
            winner = match.winner if blue_alliance_teams else None

            try:
                template_path = os.path.join(os.path.dirname(__file__), 'template.html')
                if not os.path.exists(template_path):
                    raise FileNotFoundError("The 'template.html' file was not found.")

                with open(template_path, 'r', encoding='utf-8') as file:
                    html_template = Template(file.read())

                html_content = html_template.render(
                    title="Scoreboard",
                    description="Match Details",
                    red_team_1=match.redAlliance.teamNames[0],
                    red_team_2=match.redAlliance.teamNames[1],
                    red_auto=match.redAlliance.scoreboard[2],
                    red_teleop=match.redAlliance.scoreboard[3],
                    red_endgame=match.redAlliance.scoreboard[4],
                    red_final=match.redAlliance.scoreboard[5],
                    blue_team_1=match.blueAlliance.teamNames[0],
                    blue_team_2=match.blueAlliance.teamNames[1],
                    blue_auto=match.blueAlliance.scoreboard[2],
                    blue_teleop=match.blueAlliance.scoreboard[3],
                    blue_endgame=match.blueAlliance.scoreboard[4],
                    blue_final=match.blueAlliance.scoreboard[5]
                )

                image_name = "match.png"
                hti = Html2Image(
                    browser='chrome',
                    custom_flags=[                    
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"]
                )
                img_path = hti.screenshot(html_str=html_content, size=(850, 700), save_as=image_name)[0]

                file = discord.File(img_path, filename=image_name)
                color = State.WHITE if winner == "Tie" or not blue_alliance_teams else (State.CHALLENGE_RED if winner == "Red" else State.FIRST_BLUE)
                embed = discord.Embed(title="Match Scoreboard", color=color, timestamp=datetime.now())
                embed.set_image(url=f"attachment://{image_name}")

                await interaction.followup.send(embed=embed, file=file)

            except Exception as e:
                if self.bot.debug_mode:
                    print(e)
                embed = State.ERROR(title="Error", description="An error occurred while processing the match data.")
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            if self.bot.debug_mode:
                print(e)
            embed = State.ERROR(title="Error", description="An error occurred while processing the match data.")
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(cmdMatch(bot))