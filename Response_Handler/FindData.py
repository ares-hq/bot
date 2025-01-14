from .API_Library import FirstAPI, APIParams
from datetime import datetime
from .API_Library.API_Models import Stats
import json

class FindData:
    """
    This class checks if data is in the JSON file and uses an API call to get data depending on the message.
    """
    def __init__(self, file_path="team_opr_scores_2024.json"):
        self.api_client = FirstAPI()
        self.file_path = file_path

    def set_file_path(self, file_path):
        """
        Set the file path for the JSON file.
        """
        self.file_path = file_path

    def team_info(self, team_number, year=None):
        """
        Get team information using the API.

        :param team_number: The team number.
        :param year: The year for the data.
        :return: Team information.
        """
        year = year or self.find_year()
        team_info_params = APIParams(
            path_segments=[year, 'teams'],
            query_params={'teamNumber': str(team_number)}
        )
        return self.api_client.get_team_info(team_info_params)

    def tournament_stats(self, event, year=None):
        """
        Get tournament statistics using the API.

        :param event: The event code.
        :param year: The year for the data.
        :return: Tournament statistics.
        """
        year = year or self.find_year()
        team_stats_params = APIParams(
            path_segments=[year, 'matches', event],
        )
        return self.api_client.get_team_stats_from_tournament(team_stats_params)

    def team_stats(self, team_number):
        """
        Parse a JSON file and find the key (team number) with the specified team name.

        :param team_number: The team number to search for.
        :return: The team stats if found, otherwise None.
        """
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            return data.get(str(team_number))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading JSON file: {e}")
            return None

    def team_stats_from_json(self, team_number):
        """
        Get team stats from the JSON file and convert to Stats object.

        :param team_number: The team number to search for.
        :return: Stats object with team data.
        """
        team_data = self.team_stats(team_number)
        if team_data:
            date_str = team_data.get('modifiedOn', None)
            parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            return Stats(
                teamNumber=team_number,
                autoOPR=team_data.get('autoOPR', 0.0),
                autoRank=team_data.get('autoRank', 0),
                teleOPR=team_data.get('teleOPR', 0.0),
                teleRank=team_data.get('teleRank', 0),
                endgameOPR=team_data.get('endgameOPR', 0.0),
                endgameRank=team_data.get('endgameRank', 0),
                overallOPR=team_data.get('overallOPR', 0.0),
                overallRank=team_data.get('overallRank', 0),
                penalties=team_data.get('penalties', 0.0),
                penaltyRank=team_data.get('penaltiesRank', 0),
                profileUpdate=parsed_date.strftime("%m/%d/%Y %H:%M") if date_str else "Unknown"
            )
        return Stats(teamNumber=team_number)

    @staticmethod
    def find_year():
        """
        Determine the competition year based on the current date.
        """
        current_date = datetime.now()
        return current_date.year - 1 if current_date.month < 8 else current_date.year