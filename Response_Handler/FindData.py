from .API_Library.FirstAPI import FirstAPI
from .API_Library.APIParams import APIParams
from datetime import datetime
from .API_Library.API_Models.Team import Stats
import json

'''
This class is neccesary since we need to check if data is in the JSON file, 
but also use an api call to get data depending on the message.
'''
class FindData:
    def __init__(self, file_path="team_opr_scores_2024.json"):
        self.api_client = FirstAPI()
        self.file_path = file_path
    
    def callForTeamInfo(self, teamNumber, year=None):
        year = year or self.find_year()
        team_info_params = APIParams(
            path_segments=[year, 'teams'],
            query_params={'teamNumber': str(teamNumber)}
        )
        
        return self.api_client.get_team_info(team_info_params)
    
    def callForTournamentStats(self, event, year=None):
        year = year or self.find_year()
        team_stats_params = APIParams(
            path_segments=[year, 'matches', event],
        )
        
        return self.api_client.get_team_stats_from_tournament(team_stats_params)
    
    def callForTeamStats(self, teamNumber):
        """
        Parse a JSON file and find the key (team number) with the specified team name.

        :param json_file_path: Path to the JSON file.
        :param team_name: The team name to search for.
        :return: The team number if found, otherwise None.
        """
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            return data.get(str(teamNumber))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading JSON file: {e}")
            return None
        
    def find_team_stats_from_json(self, teamNumber):
        team_data = self.callForTeamStats(teamNumber)
        if team_data:
            return Stats(
                teamNumber=teamNumber,
                autoOPR=team_data.get('Auto OPR', 0.0),
                teleOPR=team_data.get('TeleOp OPR', 0.0),
                endgameOPR=team_data.get('Endgame OPR', 0.0), # Not in JSON (Occluded from OPR Stat)
                overallOPR=team_data.get('Overall OPR', 0.0)
            )
        return Stats(teamNumber=teamNumber)

    @staticmethod
    def find_year():
        """
        Determine the competition year based on the current date.
        """
        current_date = datetime.now()
        return current_date.year - 1 if current_date.month < 8 else current_date.year