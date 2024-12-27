import discord
from discord import app_commands
from Response_Handler.HandleMessageResponse import HandleMessageResponse as msg

class cmdFavorite:
    def __init__(self, bot, visual):
        self.bot = bot
        self.visual = visual

    def setup(self):
        @self.bot.tree.command(name="favorite", description="Marks this as your favorite.")
        @app_commands.describe(team_number="The team to mark as favorite.")
        async def favorite(interaction: discord.Interaction, team_number: str):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return


            if not team_number: # Check if team number is provided
                embed = self.visual.WARNING
                embed.add_field(name="Reason:", value="Please provide a team number to set as favorite.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            try:
                team_data = msg.team_message_data(team_number)
                if not team_data:
                    embed = self.visual.WARNING
                    embed.add_field(name="Reason:", value=f"Team {team_number} does not exist. Try again.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                try:
                    await interaction.guild.me.edit(nick=f"Team {team_number} Bot")
                except discord.errors.Forbidden:
                    embed = self.visual.ERROR
                    embed.add_field(name="Reason:", value='Could not change nickname: Missing permissions')
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                embed = self.visual.SUCCESS
                embed.add_field(name="Result:", value=f"Team {team_number} has been set as the server favorite!")
                await interaction.response.send_message(embed=embed, ephemeral=False)
                if interaction.guild.id in self.bot.favorite_teams:
                    server_id = interaction.guild.id
                    self.bot.favorite_teams[server_id] = team_number

            except (KeyError, Exception) as e:
                print(e) if self.bot.debug_mode else None
                await interaction.response.send_message(embed=self.visual.ERROR, ephemeral=True)
                return