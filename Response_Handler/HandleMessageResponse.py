from Response_Handler.SupabaseHandler import SupabaseHandler
from Response_Handler.API_Models import Team
from Response_Handler.API_Models.Event import Alliance, Match

class HandleMessageResponse:
    """
    Example Usage
    -----
    
    message = HandleMessageResponse.match_message_data([14584, 284], [14584, 284])
    """
    
    @staticmethod
    def team_message_data(team_number:int, data_handler: SupabaseHandler=SupabaseHandler())->Team:
        """Returns a Team Summary Object containing the data necessary for the team message."""
        try:
            team_summary = data_handler.get_response(team_number)
            
            if not team_summary.teamNumber or team_summary.teamNumber <= 0:
                raise ValueError(f"Invalid team number {team_summary.teamNumber}")
            return team_summary
        
        except KeyError as e:
            raise KeyError(f"Error in team_message_data for team number {team_number}") from e

    def form_alliance(color:str, teams:list[int], data_handler:SupabaseHandler)->Alliance:
        """Creates an Alliance object from a list of team numbers"""
        try:
            if teams is None or len(teams) != 2:
                return Alliance(team1=None, team2=None, color=color)
            team_objects = [HandleMessageResponse.team_message_data(team, data_handler=data_handler) for team in teams]
            return Alliance(team1=team_objects[0], team2=team_objects[1], color=color)
        except Exception as e:
            print(e)
            raise ValueError(f"Error in form_alliance for color {color} with teams {teams}") from e

    @staticmethod
    def match_message_data(redAlliance:list[str], blueAlliance:list[str]=None)->Match:
        """ Returns a Match object containing 2 Alliance objects ("Red" and "Blue")."""
        try:
            redAlliance[0] = int(redAlliance[0])
            redAlliance[1] = int(redAlliance[1])
            data_handler = SupabaseHandler()

            if blueAlliance is not None and len(blueAlliance) == 2:
                blueAlliance[0] = int(blueAlliance[0])
                blueAlliance[1] = int(blueAlliance[1])
            return Match(redAlliance=HandleMessageResponse.form_alliance('Red', redAlliance, data_handler),
                         blueAlliance=HandleMessageResponse.form_alliance('Blue', blueAlliance, data_handler))
        except Exception as e:
            raise ValueError("Error in match_message_data") from e

# Example usage
# message = HandleMessageResponse.match_message_data([14584, 14584])
# print(message)
