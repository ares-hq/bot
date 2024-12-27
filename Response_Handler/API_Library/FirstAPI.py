import requests
from .APIParams import APIParams
from .API_Models.Team import Info, Stats
from .API_Models.Event import Event
import os
from dotenv import load_dotenv
from .RobotMath.MatrixMath import MatrixMath as mm
from .RobotMath.TeamMatrixBuilder import MatrixBuilder

'''
Example usage(12/23/24):

newParams = APIParams('14584')
newOneCall = FirstAPI(newParams)
team = newOneCall.get_team_data()
'''
class FirstAPI:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://ftc-api.firstinspires.org/v2.0"
        self.url_builder = URLBuilder(self.base_url)
        self.username = os.getenv('FIRST_USERNAME')
        self.password = os.getenv('FIRST_PASS')
        if not self.username or not self.password:
            raise EnvironmentError("Environment variables FIRST_USERNAME and FIRST_PASS are required.")
    
    def api_request(self, url, params=None):
        """
        Make a GET request to the API.
        """
        response = requests.get(url, auth=(self.username, self.password), params=params)
        response.raise_for_status()
        return response

    def get_team_info(self, params):
        """
        APIParams(
            path_segments=[{year}, 'teams'],
            query_params={'teamNumber': {team number}}
        )
        Get basic information about a team.
        """
        assert isinstance(params, APIParams)
        url = self.url_builder.build(params.to_path_segments())
        try:
            response = self.api_request(url, params=params.to_query_params())
        except requests.exceptions.HTTPError as e:
            return TypeError("Team not found.")

        team_data = Info()
        team_info = response.json().get('teams', [{}])[0]

        team_data.teamName = team_info.get('nameShort', "Unknown")
        team_data.location = f"{team_info.get('city', 'Unknown')}, {team_info.get('stateProv', 'Unknown')}, {team_info.get('country', 'Unknown')}"
        team_data.sponsors = str(team_info.get('nameFull', "Unknown")).replace("/", ", ").replace("&", ", ").rstrip(", ")

        return team_data
            
    def get_team_stats_from_tournament(self, params):
        """
        APIParams(
            path_segments=[{year}, 'matches', {event}],
        )
        Get statistics for teams participating in a tournament.
        """
        assert isinstance(params, APIParams)
        url = self.url_builder.build(*params.to_path_segments())
        response = self.api_request(url)
        match_data = response.json().get('matches')

        endgameParams = APIParams(
            path_segments=[params.path_segments[0], 'scores', params.path_segments[2], 'qual'],
        )

        endgameStats = self.get_endgame_stats(endgameParams)
        modified_on_match_data = {}
        for match, endgame in zip(match_data, endgameStats):
            match["scoreRedEndgame"] = endgame["red"]
            match["scoreBlueEndgame"] = endgame["blue"]

        for match in match_data:
            for team in match['teams']:
                if team['teamNumber'] not in modified_on_match_data:
                    modified_on_match_data[team['teamNumber']] = match['modifiedOn']

        matrix_builder = MatrixBuilder(match_data)
        matrix_builder.create_binary_and_score_matrices()

        event = Event()
        event.eventCode = params.to_path_segments()[2]
        
        teams_auto = mm.LSE(matrix_builder.binary_matrix, matrix_builder.auto_matrix)
        teams_tele = mm.LSE(matrix_builder.binary_matrix, matrix_builder.tele_matrix)
        teams_endgame = mm.LSE(matrix_builder.binary_matrix, matrix_builder.endgame_matrix)
        for team in matrix_builder.teams:
            team_stats = Stats()
            team_stats.teamNumber = team
            team_stats.autoOPR = teams_auto[matrix_builder.team_indices[team]]
            team_stats.teleOPR = teams_tele[matrix_builder.team_indices[team]]
            team_stats.endgameOPR = teams_endgame[matrix_builder.team_indices[team]]
            team_stats.overallOPR = team_stats.autoOPR + team_stats.teleOPR
            if len(modified_on_match_data) > 0:
                team_stats.profileUpdate = modified_on_match_data[team_stats.teamNumber]
            event.teams.append(team_stats)

        return event
    
    def get_season_events(self, year):
        """
        Get a list of events for the given season.
        """
        apiParams = APIParams(path_segments=[year, 'events'])
        url = self.url_builder.build(*apiParams.to_path_segments())
        response = self.api_request(url)
        events = response.json().get('events')
        return [event.get("code") for event in events]

    def get_last_update(self):
        """
        Get the last update time for the API.
        """
        url = self.url_builder.build('last_update')
        response = self.api_request(url)
        return response.json().get('lastUpdate')
    
    def get_endgame_stats(self, params):
        '''
        APIParams(
            path_segments=[{year}, 'scores', {event}, {tournament level}],
        )
        '''
        assert isinstance(params, APIParams)
        url = self.url_builder.build(*params.to_path_segments())
        response = self.api_request(url)
        response = response.json().get('matchScores')
        
        result = []
        for match in response:
            red_alliance = match["alliances"][1]
            blue_alliance = match["alliances"][0]

            red_sum = red_alliance["teleopParkPoints"] + red_alliance["teleopAscentPoints"]
            blue_sum = blue_alliance["teleopParkPoints"] + blue_alliance["teleopAscentPoints"]
            result.append({"matchNumber": match["matchNumber"], "red": red_sum, "blue": blue_sum})

        return result               

class URLBuilder:
    """
    A utility class for building URLs dynamically.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def build(self, *path_segments, **query_params):
        """
        Build a URL using path segments and query parameters.
        """
        if len(path_segments) == 1 and isinstance(path_segments[0], list):
            path_segments = path_segments[0]

        path = "/".join(str(segment) for segment in path_segments if segment)
        url = f"{self.base_url}/{path}" if path else self.base_url

        if query_params:
            query_string = "&".join(f"{key}={value}" for key, value in query_params.items() if value is not None)
            url = f"{url}?{query_string}"
        return url