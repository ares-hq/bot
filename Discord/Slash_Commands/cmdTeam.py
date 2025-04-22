import discord
from discord import app_commands
from discord.ext import commands
from Response_Handler import HandleMessageResponse as msg
from Response_Handler.SupabaseHandler import SupabaseHandler
from Discord.BotState import State

class cmdTeam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="team", description="Displays team information.")
    @app_commands.describe(team_number="Details about the team.")
    async def team(self, interaction: discord.Interaction, team_number: str):
        if self.bot.debug_mode and interaction.channel_id not in self.bot.debug_channel_ids:
            return

        if not team_number or not team_number.isdigit():
            embed = State.WARNING(description="Team number must be numerical.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            message = msg.team_message_data(team_number=int(team_number)).__str__()
        except Exception as e:
            if self.bot.debug_mode:
                print(e)
            embed = State.ERROR(description="Team number must be valid.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        lines = message.strip().split('\n')

        favorite_teams = self.bot.favorite_teams.get(interaction.guild.id, [])

        # Check if the team number is in the favorite teams list
        if any(team['number'] == team_number for team in favorite_teams):
            lines[0] += " ⭐"  # add star to favorite

        ######
        # Add future code to allow for favorite teams to be added and removed from the list using emojis
        # Also the ability to add teams to the future "watch" list
        ######

        embed = discord.Embed(
            title=f"Information for Team {team_number}",
            description="\n".join(lines[:-2]),
            color=State.WHITE
        )
        embed.set_footer(text="\n".join(lines[-2:]))
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(cmdTeam(bot))