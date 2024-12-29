import discord
from discord import app_commands
from discord.ext import commands
from Discord.utils import PaginationView
from Discord.BotState import State

class cmdHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays help information.")
    async def help(self, interaction: discord.Interaction):
        if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
            return

        pages = []

        landing_page = discord.Embed(
            title=f"{State.NAME} Bot Help",
            description=f"Welcome to the {State.NAME} Bot! Here you can find information about the available commands.",
            color=discord.Color.lighter_grey()
        )
        landing_page.set_thumbnail(url=self.bot.user.avatar.url)
        landing_page.add_field(name="Developers", value=State.DEVELOPERS, inline=False)
        landing_page.add_field(name="Version", value=State.VERSION, inline=False)
        pages.append(landing_page)

        for command, info in State.COMMANDS.items():
            embed = discord.Embed(
                title=f"/{command}",
                color=discord.Color.blue()
            )
            for field, value in info.items():
                if field == "Description":  # Skip the description field
                    embed.description=info["Description"]
                else:
                    embed.add_field(name=field, value=value, inline=False)
            
            pages.append(embed)

        view = PaginationView(pages)
        await interaction.response.send_message(embed=pages[0], view=view)

async def setup(bot):
    await bot.add_cog(cmdHelp(bot))