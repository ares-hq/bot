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

        red_alliance_teams = [team.strip() for team in red_alliance.split()]
        blue_alliance_teams = [team.strip() for team in blue_alliance.split()] if blue_alliance else []

        if len(red_alliance_teams) != 2 or (blue_alliance and len(blue_alliance_teams) != 2):
            embed = State.WARNING(description="Each alliance must have exactly 2 team numbers separated by a space.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            match = msg.match_message_data(red_alliance_teams, blue_alliance_teams)
            winner = match.winner if blue_alliance_teams else None

            def round_scores(scores):
                return [str(round(float(score))) if float(score) >= 0 else '0' for score in scores]

            def trim_string(string, max_length=44):
                return string[:max_length] + '...' if len(string) > max_length else string

            color = State.WHITE if winner == "Tie" or not blue_alliance_teams else (State.CHALLENGE_RED if winner == "Red" else State.FIRST_BLUE)

            embed = discord.Embed(title="Match Scoreboard", color=color, timestamp=datetime.now())
            # embed.add_field(name="Categories", value=f"```{'\n'.join(match.matchCategories)}```", inline=True)

            try:
                template_path = os.path.join(os.path.dirname(__file__), 'template.html')
                with open(template_path, 'r', encoding='utf-8') as file:
                    html_template = Template(file.read())

                event_code=None, 
                match_type=None,
                match_number=None, 

                html_content = html_template.render(title="Scoreboard",
                                                    description=f"{event_code} - {match_type} Match {match_number}",

                                                    red_team_1=match.redAlliance.teamNames[0], 
                                                    red_team_2=match.redAlliance.teamNames[1],
                                                    red_auto=match.redAlliance.scoreboard[2],
                                                    red_teleop=match.redAlliance.scoreboard[3],
                                                    red_endgame=match.redAlliance.scoreboard[4],
                                                    red_penalties=0,
                                                    red_final=match.redAlliance.scoreboard[5],

                                                    blue_team_1=match.blueAlliance.teamNames[0],
                                                    blue_team_2=match.blueAlliance.teamNames[1], 
                                                    blue_auto=match.blueAlliance.scoreboard[2],
                                                    blue_teleop=match.blueAlliance.scoreboard[3],
                                                    blue_endgame=match.blueAlliance.scoreboard[4],
                                                    blue_penalties=0,
                                                    blue_final=match.blueAlliance.scoreboard[5]
                                                )
                image_name = "match.png"
                img_path = Html2Image(browser=State.BROWSER).screenshot(html_str=html_content, size=(850, 700), save_as=image_name)[0]
                file = discord.File(img_path, filename=image_name)
                embed.set_image(url=f"attachment://{image_name}")

            except Exception as e:
                raise FileNotFoundError(f"An error occurred while generating the image: {e}")


            # if blue_alliance_teams:  # If blue alliance is provided, make full match embed
            #     embed.add_field(name="Red Alliance", value=f"```\n{'\n'.join(round_scores(match.redAlliance.scoreboard))}```", inline=True)
            #     embed.add_field(name="Blue Alliance", value=f"```\n{'\n'.join(round_scores(match.blueAlliance.scoreboard))}```", inline=True)
            #     if winner != "Tie":
            #         winner_team_1 = trim_string(f"{match.redAlliance.teamNames[0]} ({match.redAlliance.teamNums[0]})") if winner == "Red" else trim_string(f"{match.blueAlliance.teamNames[0]} ({match.blueAlliance.teamNums[0]})")
            #         winner_team_2 = trim_string(f"{match.redAlliance.teamNames[1]} ({match.redAlliance.teamNums[1]})") if winner == "Red" else trim_string(f"{match.blueAlliance.teamNames[1]} ({match.blueAlliance.teamNums[1]})")
            #         embed.add_field(name="Match Winner", value=f"```\n{match.winner} Alliance\nTeam 1: {winner_team_1}\nTeam 2: {winner_team_2}```", inline=False)
            #     else:
            #         embed.add_field(name="Match Winner", value=f"```\n{match.winner}```", inline=False)
            # else:
            #     redTeam1 = trim_string(f"{match.redAlliance.teamNames[0]}", max_length=31) + f" ({red_alliance_teams[0]})"
            #     redTeam2 = trim_string(f"{match.redAlliance.teamNames[1]}", max_length=31) + f" ({red_alliance_teams[1]})"
            #     embed.add_field(name="Alliance", value=f"```\n{redTeam1}\n{redTeam2}\n{'\n'.join(round_scores(match.redAlliance.scoreboard[2:]))}```", inline=True)

            if self.bot.debug_mode:
                print(match.__str__().strip())

            await interaction.response.send_message(embed=embed, file=file)

        except Exception as e:
            if self.bot.debug_mode:
                print(e)
            embed = State.ERROR(title="Error", description="An error occurred while processing the match data.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

async def setup(bot):
    await bot.add_cog(cmdMatch(bot))