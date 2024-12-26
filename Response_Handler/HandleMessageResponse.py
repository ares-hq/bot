from .API_Library.API_Models.Event import Alliance, Match
from .FindData import FindData

class HandleMessageResponse:
    """
    Example Usage
    -----
    
    message = HandleMessageResponse.match_message_data([1454, 284], [1454, 284]) \n
    """
    
    @staticmethod
    def team_message_data(teamNumber):
        """
        Returns a Team Summary Object containing the data necessary for the team message.

        """
        find_team_data = FindData("world_opr_scores_.json")
        try:
            team_stats = find_team_data.team_stats_from_json(teamNumber)
            team_info = find_team_data.TeamInfo(teamNumber)
            
            if team_info and team_stats is not None:
                return (team_stats + team_info) # Summary Object
            else:
                raise KeyError("Data message not found.")
        except KeyError as e:
            return e

    @staticmethod
    def get_team_stats(team):
        try:
            return HandleMessageResponse.team_message_data(team)['stats']
        except KeyError as e:
            return e

    @staticmethod
    def form_alliance(color, teams):
        """Creates an Alliance object from a list of team numbers"""
        team_objects = [HandleMessageResponse.get_team_stats(team) for team in teams]
        if len(team_objects) != 2:
            return ValueError("Alliances are required to have exactly two teams.")
        return Alliance(team1=team_objects[0], team2=team_objects[1], color=color)

    @staticmethod
    def match_message_data(redAlliance, blueAlliance=None):
        """
        Returns a Match object containing the data necessary for the match message.

        Args:
            redAlliance (list): List of team numbers for the red alliance.
            blueAlliance (list, optional): List of team numbers for the blue alliance. Defaults to None.

        Returns:
            Match: A Match object containing the red and blue alliances.
        """
        if len(redAlliance) > 2 or (blueAlliance is not None and len(blueAlliance) > 2):
            return ValueError("Exactly two teams are required to form an alliance.")

        red_alliance = HandleMessageResponse.form_alliance('Red', redAlliance)
        blue_alliance = HandleMessageResponse.form_alliance('Blue', blueAlliance) if blueAlliance else None

        return Match(redAlliance=red_alliance, blueAlliance=blue_alliance) if blueAlliance else red_alliance