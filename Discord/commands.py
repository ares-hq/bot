import discord
from discord import app_commands
from discord.ext import commands
from .utils import PaginationView, create_multi_page_embed as create_mpe
from Response_Handler.HandleMessageResponse import HandleMessageResponse as msg

#####################################################
# Feature Request (API):
# - Tournament Schedule Given a Event Code
# - Team Schedule Given a Team Number
# - Tournament Mode - Live Scoring
# 
# Feature Request (Local Scouting):
# - Manual Scouting
# -- Sample Cycles (Samples, Specimens)
# -- Robot Speed (Fast, Medium, Slow)
# -- Hang Potential (Level 1,2,3, Park)
# -- Specialized? (Samples, Specimens, Both, None)
# -- Autonomous (Yes, No)
#####################################################

class Commands:
    def __init__(self, bot):
        self.bot = bot

    def setup_commands(self):
        self.slash_team()
        self.slash_match()
        self.slash_favorite()
        # self.slash_tournament_schedule()
        # self.slash_team_schedule()
        # self.slash_live_scoring()
        # self.slash_list_events()
        self.slash_help()

    def process_alliance(self, alliance: str) -> list:
        return [team.strip() for team in alliance.split(",")]

    def slash_team(self):
        @self.bot.tree.command(name="team", description="Displays team information.")
        @app_commands.describe(team_number="Details about the team.")
        async def team(interaction: discord.Interaction, team_number: str = None):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return
            
            try:
                message = msg.team_message_data(team_number).__str__()
            except Exception as e:
                print(e) if self.bot.debug_mode else None
                message = "Data cannot be found at this time. Try again later."

            embed = discord.Embed(
                title=f"Information for Team {team_number}",
                description=message,
                color=discord.Color.lighter_grey()
            )

            # Fetch the avatar image
            # url = None  # Initialize the url variable
            # css_content = requests.get('https://ftc-scoring.firstinspires.org/avatars/composed/2025.css').text
            # match = re.search(rf'\.team-{team_number} \{{\s*background-image: url\("(?P<url>data:image/png;base64,[^"]+)"\);', css_content)
            # if match:
            #     url = match.group("url")
            
            # if url and url.startswith("data:image/png;base64,"):
            #     embed.set_thumbnail(url=url)
            # else:
            #     embed.set_thumbnail(url="https://via.placeholder.com/150")

            embed.set_footer(text="Use /team <team_number> for specific team details.")
            await interaction.response.send_message(embed=embed)

    def slash_match(self):
        @self.bot.tree.command(name="match", description="Displays match details.")
        @app_commands.describe(red_alliance="Red Alliance team numbers (space-separated).", blue_alliance="Blue Alliance team numbers (space-separated, optional).")
        async def match(interaction: discord.Interaction, red_alliance: str, blue_alliance: str = None):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return

            red_alliance_teams = [team.strip() for team in red_alliance.split()]
            blue_alliance_teams = [team.strip() for team in blue_alliance.split()] if blue_alliance else []

            if len(red_alliance_teams) != 2 or (blue_alliance and len(blue_alliance_teams) != 2):
                await interaction.response.send_message("Each alliance must have exactly 2 team numbers separated by a space.\n", ephemeral=True)
                return

            try:
                message = msg.match_message_data(red_alliance_teams, blue_alliance_teams).__str__()
            except Exception as e:
                print(e) if self.bot.debug_mode else None
                message = "Data cannot be found at this time. Try again later."

            # embed = discord.Embed(
            #     title=f"Match Summary",
            #     description=message,
            #     color=discord.Color.lighter_grey()
            # )

            # Embed setup
            
            
            # Add fields for red and blue columns
                    # Add fields for red and blue columns

            if '||' in message:
                red_message, blue_message = message.split('||')
                embed = discord.Embed(
                                        title="Scoreboard",
                                        description=f"```diff\n- {red_message}\n``` ```yaml\n{blue_message}\n```",
                                        color=discord.Color.lighter_grey()
                )
            else:
                embed = discord.Embed(
                                        title="Scoreboard",
                                        description=f"```diff\n- {message}\n```",
                                        color=discord.Color.lighter_grey()
                )

                

            # embed = discord.Embed(
            #     title=f"Match {match_data['match_number']} - {match_data['event_name']}",
            #     description=f"**Match Time:** {match_data['match_time']}",
            #     color=discord.Color.from_str('#ED1C24')
            # )

            embed.set_footer(text="Use /match <red_alliance> <blue_alliance> for specific match details.")
            await interaction.response.send_message(embed=embed)

    def slash_favorite(self):
        @self.bot.tree.command(name="favorite", description="Marks this as your favorite.")
        @app_commands.describe(team_number="The team to mark as favorite.")
        async def favorite(interaction: discord.Interaction, team_number: str):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return

            try:
                team_data = msg.team_message_data(team_number)
                if not team_data:
                    await interaction.response.send_message(f"Team {team_number} does not exist. Try again.", ephemeral=True)
                    return

                try:
                    await interaction.guild.me.edit(nick=f"Team {team_number} Bot")
                except discord.errors.Forbidden:
                    out = 'Could not change nickname: Missing permissions'
                    await interaction.response.send_message(out, ephemeral=True)
                    return

                await interaction.response.send_message(f"Team {team_number} has been set as the server favorite!", ephemeral=True)
                if interaction.guild.id in self.bot.favorite_teams:
                    server_id = interaction.guild.id
                    self.bot.favorite_teams[server_id] = team_number

            except (KeyError,Exception) as e:
                print(e) if self.bot.debug_mode else None
                await interaction.response.send_message(f"Team {team_number} does not exist. Try again.", ephemeral=True)

    def slash_tournament_schedule(self):
        @self.bot.tree.command(name="tournament_schedule", description="Displays tournament schedule given an event code.")
        @app_commands.describe(event_code="The event code for the tournament.")
        async def tournament_schedule(interaction: discord.Interaction, event_code: str):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return

            # Pseudo-code for handling tournament schedule
            # schedule = get_tournament_schedule(event_code)
            schedule = [
                "Match 1: Team A vs Team B",
                "Match 2: Team C vs Team D",
                "Match 3: Team E vs Team F",
                "Match 4: Team G vs Team H",
                "Match 5: Team I vs Team J",
                "Match 6: Team K vs Team L",
                "Match 7: Team M vs Team N",
                "Match 8: Team O vs Team P",
                "Match 9: Team Q vs Team R",
                "Match 10: Team S vs Team T"
            ]  # Replace with actual implementation

            pages = create_mpe(
                title="Tournament Schedule",
                description_list=schedule,
                color=discord.Color.blue(),
                items_per_page=10
            )

            view = PaginationView(pages)
            await interaction.response.send_message(embed=pages[0], view=view)

    def slash_team_schedule(self):
        @self.bot.tree.command(name="team_schedule", description="Displays team schedule given a team number.")
        @app_commands.describe(team_number="The team number.")
        async def team_schedule(interaction: discord.Interaction, team_number: str):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return

            # Pseudo-code for handling team schedule
            # schedule = get_team_schedule(team_number)
            schedule = "Sample Team Schedule"  # Replace with actual implementation
            await interaction.response.send_message(schedule)

    def slash_live_scoring(self):
        @self.bot.tree.command(name="live_scoring", description="Displays live scoring for the tournament.")
        async def live_scoring(interaction: discord.Interaction):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return

            # Pseudo-code for handling live scoring
            # live_scores = get_live_scoring()
            live_scores = "Sample Live Scoring"  # Replace with actual implementation
            await interaction.response.send_message(live_scores)

    def slash_list_events(self):
        @self.bot.tree.command(name="list_events", description="Lists events at the tournament.")
        async def list_events(interaction: discord.Interaction):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return

            # Pseudo-code for listing events
            # events = get_list_of_events()
            events = "Sample List of Events"  # Replace with actual implementation
            await interaction.response.send_message(events)

    def slash_help(self):
        @self.bot.tree.command(name="help", description="Displays help information.")
        async def help(interaction: discord.Interaction):
            if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
                return
            
            commands_info = {
                "team": {
                    "description": "Displays team information.",
                    "usage": "/team <team_number>"
                },
                "match": {
                    "description": "Displays match details.",
                    "usage": "/match <red_alliance> <blue_alliance>"
                },
                "favorite": {
                    "description": "Marks this as your favorite.",
                    "usage": "/favorite <team_number>"
                },
                # "tournament_schedule": {
                #     "description": "Displays tournament schedule given an event code.",
                #     "usage": "/tournament_schedule <event_code>"
                # },
                # "team_schedule": {
                #     "description": "Displays team schedule given a team number.",
                #     "usage": "/team_schedule <team_number>"
                # },
                # "live_scoring": {
                #     "description": "Displays live scoring for the tournament.",
                #     "usage": "/live_scoring"
                # },
                # "list_events": {
                #     "description": "Lists events at the tournament.",
                #     "usage": "/list_events"
                # }
            }

            pages = []

            # Landing page
            landing_page = discord.Embed(
                title="FTCScout Bot Help",
                description="Welcome to the FTCScout Bot! Here you can find information about the available commands.",
                color=discord.Color.lighter_grey()
            )
            landing_page.set_thumbnail(url=self.bot.user.avatar.url)
            landing_page.add_field(name="Developers", value="<@291420737204649985> and <@751915057973035058>", inline=False)
            landing_page.add_field(name="Version", value="v2.0.0", inline=False)
            pages.append(landing_page)

            # Generate help pages dynamically
            for command, info in commands_info.items():
                embed = discord.Embed(
                    title=f"/{command}",
                    description=info["description"],
                    color=discord.Color.blue()
                )
                embed.add_field(name="Usage", value=info["usage"], inline=False)
                pages.append(embed)

            # Pagination view
            view = PaginationView(pages)
            await interaction.response.send_message(embed=pages[0], view=view)