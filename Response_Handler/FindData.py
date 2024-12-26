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
    
    file_path = "team_opr_scores_2024.json"
    
    def set_file_path(self, file_path):
        self.file_path = file_path
    
    def TeamInfo(self, teamNumber, year=None):
        year = year or self.find_year()
        team_info_params = APIParams(
            path_segments=[year, 'teams'],
            query_params={'teamNumber': str(teamNumber)}
        )
        
        return self.api_client.get_team_info(team_info_params)
    
    def TournamentStats(self, event, year=None):
        year = year or FindData.find_year()
        team_stats_params = APIParams(
            path_segments=[year, 'matches', event],
        )
        
        return self.api_client.get_team_stats_from_tournament(team_stats_params)
    
    def TeamStats(self, teamNumber):
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
    
    def team_stats_from_json(self, teamNumber):
        team_data = self.TeamStats(teamNumber)
        if team_data:
            date_str = team_data.get('modifiedOn', None)
            parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            return Stats(
                teamNumber=teamNumber,
                autoOPR=team_data.get('autoOPR', 0.0),
                autoRank=team_data.get('autoRank', 0),
                teleOPR=team_data.get('teleOPR', 0.0),
                teleRank=team_data.get('teleRank', 0),
                endgameOPR=team_data.get('endgameOPR', 0.0),
                endgameRank=team_data.get('endgameRank', 0),
                overallOPR=team_data.get('overallOPR', 0.0),
                overallRank=team_data.get('overallRank', 0),
                profileUpdate = parsed_date.strftime("%m/%d/%Y %H:%M")
            )
        return Stats(teamNumber=teamNumber)

    @staticmethod
    def find_year():
        """
        Determine the competition year based on the current date.
        """
        current_date = datetime.now()
        return current_date.year - 1 if current_date.month < 8 else current_date.year