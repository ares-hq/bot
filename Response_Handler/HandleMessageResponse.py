from .API_Library.API_Models.Team import Stats, Info,Summary
from .API_Library.API_Models.Event import Alliance, Match
from .FindData import FindData

class HandleMessageResponse:
    """
    Example Usage
    -----
    
    message = HandleMessageResponse.match_message_data([1454, 284], [1454, 284]) \n
    """
    
    @staticmethod
    def team_message_data(teamNumber:str)->Summary:
        """Returns a Team Summary Object containing the data necessary for the team message."""
        data_search = FindData()
        try:
            team_summary = (data_search.find_team_stats_from_json(teamNumber) + 
                            data_search.callForTeamInfo(teamNumber))
            
            if team_summary.info is None:
                raise KeyError(f"Missing data - Team Info")
            elif team_summary.stats is None:
                raise KeyError(f"Missing data - Team Stats")
                   
            return  team_summary # Summary Object
        
        except KeyError as e:
            raise KeyError(f"Error in team_message_data for team number {teamNumber}") from e

    def form_alliance(color:str, teams:list[str])->Alliance:
        """Creates an Alliance object from a list of team numbers"""
        try:
            if teams is None or len(teams) != 2:
                return Alliance(team1=None, team2=None, color=color)
            team_objects = [HandleMessageResponse.team_message_data(team) for team in teams]
            alliance = Alliance(team1=team_objects[0], team2=team_objects[1], color=color)
            # print(alliance.team1, alliance.team2)
            return alliance
        except Exception as e:
            raise ValueError(f"Error in form_alliance for color {color} with teams {teams}") from e

    @staticmethod
    def match_message_data(redAlliance:list[str], blueAlliance:list[str]=None)->Match:
        """ Returns a Match object containing 2 Alliance objects ("Red" and "Blue")."""
        try:
            # print(redAlliance, blueAlliance)
            match = Match(redAlliance=HandleMessageResponse.form_alliance('Red', redAlliance),
                         blueAlliance=HandleMessageResponse.form_alliance('Blue', blueAlliance))
            # print(match.__str__())
            return match
        except Exception as e:
            raise ValueError("Error in match_message_data") from e

# Example usage
# message = HandleMessageResponse.match_message_data([14584, 14584])
# print(message)