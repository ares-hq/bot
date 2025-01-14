from .API_Library.API_Models import Summary, Alliance, Match
from .FindData import FindData

class HandleMessageResponse:
    """
    Example Usage
    -----
    
    message = HandleMessageResponse.match_message_data([1454, 284], [1454, 284]) \n
    """
    
    @staticmethod
    def team_message_data(team_number:str)->Summary:
        """Returns a Team Summary Object containing the data necessary for the team message."""
        find_data = FindData("world_opr_scores_.json")
        try:
            team_summary = (find_data.team_stats_from_json(team_number) + 
                            find_data.team_info(team_number))
            
            if team_summary.info is None:
                raise KeyError(f"Missing data - Team Info")
            elif team_summary.stats is None:
                raise KeyError(f"Missing data - Team Stats")
            
            # Check if all float values in stats are zero
            if all(getattr(team_summary.stats, attr) == 0.0 for attr in ['autoOPR', 'teleOPR', 'endgameOPR', 'overallOPR', 'Penalties']):
                raise ValueError(f"All float values in team stats are zero for team number {team_number}")
            
            # Check if team number is empty or zero
            if not team_summary.stats.teamNumber or team_summary.stats.teamNumber == 0:
                raise ValueError(f"Invalid team number {team_summary.stats.teamNumber}")
                   
            return team_summary # Summary Object
        
        except KeyError as e:
            raise KeyError(f"Error in team_message_data for team number {team_number}") from e

    def form_alliance(color:str, teams:list[str])->Alliance:
        """Creates an Alliance object from a list of team numbers"""
        try:
            if teams is None or len(teams) != 2:
                return Alliance(team1=None, team2=None, color=color)
            
            team_objects = [HandleMessageResponse.team_message_data(team) for team in teams]

            return Alliance(team1=team_objects[0], team2=team_objects[1], color=color)
        except Exception as e:
            raise ValueError(f"Error in form_alliance for color {color} with teams {teams}") from e

    @staticmethod
    def match_message_data(redAlliance:list[str], blueAlliance:list[str]=None)->Match:
        """ Returns a Match object containing 2 Alliance objects ("Red" and "Blue")."""
        try:
            return Match(redAlliance=HandleMessageResponse.form_alliance('Red', redAlliance),
                         blueAlliance=HandleMessageResponse.form_alliance('Blue', blueAlliance))
        except Exception as e:
            raise ValueError("Error in match_message_data") from e

# Example usage
# message = HandleMessageResponse.match_message_data([14584, 14584])
# print(message)
