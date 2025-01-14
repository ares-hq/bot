import os
import requests
from dotenv import load_dotenv
from .APIParams import APIParams
from .API_Models import Info, Stats, Event
from Response_Handler.API_Library.API_Models.Event import Event
from .RobotMath import MatrixBuilder, MatrixMath as mm

'''
Example usage(12/28/24):

newParams = APIParams('14584')
newOneCall = FirstAPI(newParams)
team = newOneCall.get_team_data()
'''
class FirstAPI:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://ftc-api.firstinspires.org/v2.0"
        self.username = os.getenv('FIRST_USERNAME')
        self.password = os.getenv('FIRST_PASS')
        if not self.username or not self.password:
            raise EnvironmentError("Environment variables FIRST_USERNAME and FIRST_PASS are required.")
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    def api_request(self, path_segments, params=None):
        """
        Make a GET request to the API.
        """
        url = self.build_url(path_segments)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def build_url(self, path_segments):
        """
        Build a URL using path segments.
        """
        path = "/".join(str(segment) for segment in path_segments if segment)
        return f"{self.base_url}/{path}"

    def get_team_info(self, params) -> Info:
        """
        Get basic information about a team.
        """
        assert isinstance(params, APIParams)
        response = self.api_request(params.to_path_segments(), params=params.to_query_params())
        team_info = response.get('teams', [{}])[0]
        return Info(
            teamName=team_info.get('nameShort', "Unknown"),
            sponsors=str(team_info.get('nameFull', "Unknown")).replace("/", ", ").replace("&", ", ").rstrip(", "),
            location=f"{team_info.get('city', 'Unknown')}, {team_info.get('stateProv', 'Unknown')}, {team_info.get('country', 'Unknown')}"
        )

    def get_team_stats_from_tournament(self, params):
        """
        Get statistics for teams participating in a tournament.
        """
        assert isinstance(params, APIParams)
        match_data = self.api_request(params.to_path_segments())
        match_data = match_data.get('matches', [])

        point_breakdown_params = APIParams(
            path_segments=[params.path_segments[0], 'scores', params.path_segments[2], 'qual'],
        )
        endgame_stats = self.get_endgame_stats(point_breakdown_params)
        penalties = self.get_penalties(point_breakdown_params)
        
        modified_on_match_data = {}

        for match, endgame, penalty in zip(match_data, endgame_stats, penalties):
            match["scoreRedEndgame"] = endgame["red"]
            match["scoreBlueEndgame"] = endgame["blue"]
            match["penaltyPointsRed"] = penalty["red"]
            match["penaltyPointsBlue"] = penalty["blue"]

        for match in match_data:
            for team in match['teams']:
                if team['teamNumber'] not in modified_on_match_data:
                    modified_on_match_data[team['teamNumber']] = match['modifiedOn']

        matrix_builder = MatrixBuilder(match_data)
        matrix_builder.create_binary_and_score_matrices()

        event = Event(eventCode=params.path_segments[2])
        teams_auto = mm.LSE(matrix_builder.binary_matrix, matrix_builder.auto_matrix)
        teams_tele = mm.LSE(matrix_builder.binary_matrix, matrix_builder.tele_matrix)
        teams_endgame = mm.LSE(matrix_builder.binary_matrix, matrix_builder.endgame_matrix)
        teams_penalties = mm.LSE(matrix_builder.binary_matrix, matrix_builder.penalties_matrix)

        for team in matrix_builder.teams:
            team_stats = Stats(
                teamNumber=team,
                autoOPR=teams_auto[matrix_builder.team_indices[team]],
                teleOPR=teams_tele[matrix_builder.team_indices[team]],
                endgameOPR=teams_endgame[matrix_builder.team_indices[team]],
                overallOPR=teams_auto[matrix_builder.team_indices[team]] + teams_tele[matrix_builder.team_indices[team]],
                penalties=teams_penalties[matrix_builder.team_indices[team]],
                profileUpdate=modified_on_match_data.get(team, "Unknown")
            )
            event.teams.append(team_stats)

        return event

    def get_season_events(self, year):
        """
        Get a list of events for the given season.
        """
        api_params = APIParams(path_segments=[year, 'events'])
        response = self.api_request(api_params.to_path_segments())
        events = response.get('events', [])
        return [event.get("code") for event in events]

    def get_last_update(self):
        """
        Get the last update time for the API.
        """
        response = self.api_request(['last_update'])
        return response.get('lastUpdate')

    def get_endgame_stats(self, params):
        """
        Get endgame statistics for a tournament.
        """
        assert isinstance(params, APIParams)
        response = self.api_request(params.to_path_segments())
        match_scores = response.get('matchScores', [])

        result = []
        for match in match_scores:
            red_alliance = match["alliances"][1]
            blue_alliance = match["alliances"][0]
            red_sum = red_alliance["teleopParkPoints"] + red_alliance["teleopAscentPoints"]
            blue_sum = blue_alliance["teleopParkPoints"] + blue_alliance["teleopAscentPoints"]
            result.append({"matchNumber": match["matchNumber"], "red": red_sum, "blue": blue_sum})

        return result
    
    def get_penalties(self, params):
        """
        Get penalty statistics for a tournament.
        """
        assert isinstance(params, APIParams)
        response = self.api_request(params.to_path_segments())
        match_scores = response.get('matchScores', [])
        
        result = []
        for match in match_scores:
            red_alliance = match["alliances"][1]
            blue_alliance = match["alliances"][0]
            red_sum = red_alliance["foulPointsCommitted"]
            blue_sum = blue_alliance["foulPointsCommitted"]
            result.append({"matchNumber": match["matchNumber"], "red": red_sum, "blue": blue_sum})

        return result
                  

# class URLBuilder:
#     """
#     A utility class for building URLs dynamically.
#     """
#     def __init__(self, base_url):
#         self.base_url = base_url

#     def build(self, *path_segments, **query_params):
#         """
#         Build a URL using path segments and query parameters.
#         """
#         if len(path_segments) == 1 and isinstance(path_segments[0], list):
#             path_segments = path_segments[0]

#         path = "/".join(str(segment) for segment in path_segments if segment)
#         url = f"{self.base_url}/{path}" if path else self.base_url

#         if query_params:
#             query_string = "&".join(f"{key}={value}" for key, value in query_params.items() if value is not None)
#             url = f"{url}?{query_string}"
#         return url