import discord
from discord import app_commands
from discord.ext import commands
from Response_Handler import HandleMessageResponse as msg
from Discord.BotState import State

class cmdFavorite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.visual = State()

    @app_commands.command(name="favorite", description="Marks this as your favorite or shows favorite teams.")
    @app_commands.describe(team_number="The team to mark as favorite.")
    async def favorite(self, interaction: discord.Interaction, team_number: str = None):
        if self.bot.debug_mode and interaction.channel_id not in self.bot.debug_channel_ids:
            return

        server_id = interaction.guild.id

        if not team_number:  # Check if team number is provided
            await self.show_favorite_teams(interaction, server_id)
            return

        await self.update_favorite_team(interaction, server_id, team_number)

    async def show_favorite_teams(self, interaction: discord.Interaction, server_id: int):
        favorite_teams = self.bot.favorite_teams.get(server_id, [])

        embed = discord.Embed(title="Favorite Teams", color=State.FAVORITE)
        if not favorite_teams:
            embed.description = "No favorite teams set."
            embed.set_footer(text="Run the command with a team number to add it to favorites.")
        else:
            embed.description = "\n".join([f"{team['name']} ({team['number']}) ⭐" for team in favorite_teams])
            embed.set_footer(text="Re-run the command with a team number to remove it from favorites.")

        await interaction.response.send_message(embed=embed, ephemeral=False)

    async def update_favorite_team(self, interaction: discord.Interaction, server_id: int, team_number: str):
        try:
            team_data = msg.team_message_data(team_number)
            if not team_data:
                embed = State.WARNING(title="Warning", description=f"Team {team_number} does not exist. Try again.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            favorite_teams = self.bot.favorite_teams.setdefault(server_id, [])
            value = {"name": team_data.info.teamName, "number": team_number}  # Store as a dictionary

            # Check if the team_number is in the favorite_teams list
            if any(team['number'] == team_number for team in favorite_teams):
                # Remove the team if it already exists
                favorite_teams = [team for team in favorite_teams if team['number'] != team_number]
            else:
                # Add the team if it doesn't exist
                favorite_teams.append(value)

            self.bot.favorite_teams[server_id] = favorite_teams  # Update the favorite teams list

            await self.show_favorite_teams(interaction, server_id)

        except Exception as e:
            if self.bot.debug_mode:
                print(e)
            embed = State.ERROR(title="Error", description="Team Number must be valid.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(cmdFavorite(bot))