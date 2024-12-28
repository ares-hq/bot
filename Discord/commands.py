from .Slash_Commands import cmdMatch, cmdTeam, cmdFavorite, cmdHelp, cmdDeveloper
from .BotState import State

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
        self.visual = State()

    async def setup(self):
        try:
            for cmd in (
                cmdTeam(self.bot),
                cmdMatch(self.bot),
                cmdFavorite(self.bot),
                cmdHelp(self.bot),
                cmdDeveloper(self.bot)
            ):
                await self.bot.add_cog(cmd)
            print("Slash Commands Setup Complete.")
        except Exception as e:
            print(f"Failed to setup commands: {e}")



        ## WORK IN PROGRESS ##
        ## TO BE MOVED TO SEPARATE FILE ##

        # self.slash_tournament_schedule()
        # self.slash_team_schedule()
        # self.slash_live_scoring()
        # self.slash_list_events()

    # def slash_tournament_schedule(self):
    #     @self.bot.tree.command(name="tournament_schedule", description="Displays tournament schedule given an event code.")
    #     @app_commands.describe(event_code="The event code for the tournament.")
    #     async def tournament_schedule(interaction: discord.Interaction, event_code: str):
    #         if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
    #             return

    #         # Pseudo-code for handling tournament schedule
    #         # schedule = get_tournament_schedule(event_code)
    #         schedule = [
    #             "Match 1: Team A vs Team B",
    #             "Match 2: Team C vs Team D",
    #             "Match 3: Team E vs Team F",
    #             "Match 4: Team G vs Team H",
    #             "Match 5: Team I vs Team J",
    #             "Match 6: Team K vs Team L",
    #             "Match 7: Team M vs Team N",
    #             "Match 8: Team O vs Team P",
    #             "Match 9: Team Q vs Team R",
    #             "Match 10: Team S vs Team T"
    #         ]  # Replace with actual implementation

    #         pages = create_mpe(
    #             title="Tournament Schedule",
    #             description_list=schedule,
    #             color=discord.Color.blue(),
    #             items_per_page=10
    #         )

    #         view = PaginationView(pages)
    #         await interaction.response.send_message(embed=pages[0], view=view)

    # def slash_team_schedule(self):
    #     @self.bot.tree.command(name="team_schedule", description="Displays team schedule given a team number.")
    #     @app_commands.describe(team_number="The team number.")
    #     async def team_schedule(interaction: discord.Interaction, team_number: str):
    #         if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
    #             return

    #         # Pseudo-code for handling team schedule
    #         # schedule = get_team_schedule(team_number)
    #         schedule = "Sample Team Schedule"  # Replace with actual implementation
    #         await interaction.response.send_message(schedule)

    # def slash_live_scoring(self):
    #     @self.bot.tree.command(name="live_scoring", description="Displays live scoring for the tournament.")
    #     async def live_scoring(interaction: discord.Interaction):
    #         if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
    #             return

    #         # Pseudo-code for handling live scoring
    #         # live_scores = get_live_scoring()
    #         live_scores = "Sample Live Scoring"  # Replace with actual implementation
    #         await interaction.response.send_message(live_scores)

    # def slash_list_events(self):
    #     @self.bot.tree.command(name="list_events", description="Lists events at the tournament.")
    #     async def list_events(interaction: discord.Interaction):
    #         if self.bot.debug_mode and interaction.channel_id != self.bot.debug_channel_id:
    #             return

    #         # Pseudo-code for listing events
    #         # events = get_list_of_events()
    #         events = "Sample List of Events"  # Replace with actual implementation
    #         await interaction.response.send_message(events)
