from API_Library.FirstAPI import FirstAPI
from API_Library.APIParams import APIParams
from datetime import datetime
from API_Library.API_Models.Team import Stats
import json

'''
This class is neccesary since we need to check if data is in the JSON file, 
but also use an api call to get data depending on the message.
'''
class FindData:
    def __init__(self):
        self.api_client = FirstAPI()
        self.file_path = "team_opr_scores_2024.json"
    
    def callForTeamInfo(self, teamNumber, year=None):
        team_info_params = APIParams(
            path_segments=[FindData.find_year() if year is None else year, 'teams'],
            query_params={'teamNumber': str(teamNumber)}
        )
        
        return self.api_client.get_team_info(team_info_params)
    
    def callForTournamentStats(self, event, year=None):
        team_stats_params = APIParams(
            path_segments=[FindData.find_year() if year is None else year, 'matches', event],
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

            if str(teamNumber) in data:
                return data[str(teamNumber)]

            return None

        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {self.file_path}")
            return None
        
    def find_team_stats_from_json(self, teamNumber):
        team_data = self.callForTeamStats(teamNumber)
        team_stats = Stats()
        if team_data is not None:
            team_stats.autoOPR = team_data['Auto OPR']
            team_stats.teleOPR = team_data['TeleOp OPR']
            team_stats.overallOPR = team_data['Overall OPR']
        
        return team_stats

    @staticmethod
    def find_year():
        """
        Determine the competition year based on the current date.
        """
        current_date = datetime.now()
        return current_date.year - 1 if current_date.month < 8 else current_date.year