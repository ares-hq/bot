import discord
from discord import app_commands
from Response_Handler.HandleMessageResponse import HandleMessageResponse as msg

from Discord.utils import PaginationView

class cmdHelp:
    def __init__(self, bot, visual):
        self.bot = bot
        self.visual = visual

    def setup(self):
        @self.bot.tree.command(name="help", description="Displays help information.")
        async def help(interaction: discord.Interaction):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return
            
            commands_info = {
                "team": {
                    "description": "Displays team *FIRST* information",
                    "usage": "/team <team_number>"
                },
                "match": {
                    "description": "OPR-Based Match Prediction",
                    "usage": "/match <red_alliance> <blue_alliance>"
                },
                "favorite": {
                    "description": "Marks a team as the server favorite.\n*This will change the bot's nickname*",
                    "usage": "/favorite <team_number>"
                }
            }

            pages = []

            landing_page = discord.Embed(
                title="FTCScout Bot Help",
                description="Welcome to the FTCScout Bot! Here you can find information about the available commands.",
                color=discord.Color.lighter_grey()
            )
            landing_page.set_thumbnail(url=self.bot.user.avatar.url)
            landing_page.add_field(name="Developers", value="<@291420737204649985> and <@751915057973035058>", inline=False)
            landing_page.add_field(name="Version", value="v2.0.0", inline=False)
            pages.append(landing_page)

            for command, info in commands_info.items():
                embed = discord.Embed(
                    title=f"/{command}",
                    description=info["description"],
                    color=discord.Color.blue()
                )
                embed.add_field(name="Usage", value=info["usage"], inline=False)
                pages.append(embed)

            view = PaginationView(pages)
            await interaction.response.send_message(embed=pages[0], view=view)