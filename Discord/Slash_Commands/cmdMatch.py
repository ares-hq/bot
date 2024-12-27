import discord
from discord import app_commands
from Response_Handler.HandleMessageResponse import HandleMessageResponse as msg
from dataclasses import fields
from datetime import datetime

class cmdMatch:
    def __init__(self, bot, visual):
        self.bot = bot
        self.visual = visual

    def setup(self):
        @self.bot.tree.command(name="match", description="Displays match details.")
        @app_commands.describe(red_alliance="Red Alliance team numbers (space-separated).", blue_alliance="Blue Alliance team numbers (space-separated, optional).")
        async def match(interaction: discord.Interaction, red_alliance: str, blue_alliance: str = None):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return

            red_alliance_teams = [team.strip() for team in red_alliance.split()]
            blue_alliance_teams = [team.strip() for team in blue_alliance.split()] if blue_alliance else []

            if len(red_alliance_teams) != 2 or (blue_alliance and len(blue_alliance_teams) != 2):
                embed = self.visual.WARNING
                embed.add_field(name="Reason:", value="Each alliance must have exactly 2 team numbers separated by a space.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            try:
                match = msg.match_message_data(red_alliance_teams, blue_alliance_teams).__str__()

                match_str = match
                embed = discord.Embed(title="Match Scoreboard", color=discord.Color.lighter_grey(),timestamp=datetime.now())
                embed.add_field(name="Categories", value=match_str[0], inline=True)
                embed.add_field(name="Red Alliance", value=match_str[1], inline=True)
                embed.add_field(name="Blue Alliance", value=match_str[2], inline=True)
                embed.add_field(name="Match Winner", value=match_str[3], inline=False)

            except Exception as e:
                print(e) if self.bot.debug_mode else None
                await interaction.response.send_message(embed=self.visual.ERROR, ephemeral=True)
                return
            
        
            # embed.set_footer(text="Use /match <red_alliance> <blue_alliance> for specific match details.")
            await interaction.response.send_message(embed=embed)

