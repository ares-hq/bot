from concurrent.futures import ThreadPoolExecutor
from API_Library.APIClient import APIClient
from API_Library.APIParams import APIParams
from API_Library.API_Models.Team import Team
from API_Library.API_Models.Event import Event
from API_Library.API_Models.Season import Season
from API_Library.RobotMath import MatrixBuilder, MatrixMath as mm
from datetime import datetime
from tqdm import tqdm

class FirstAPI:
    def __init__(self):
        base_url = "https://ftc-api.firstinspires.org/v2.0"
        self.client = APIClient(base_url)

    def get_season_events(self, year: int):
        """
        Fetch a list of events for the given season.
        :param year: The year for which to fetch events.
        :return: List of event codes.
        """
        params = APIParams(path_segments=[year, 'events'])
        response = self.client.api_request(params)
        return [event.get("code") for event in response.get('events', [])]

    def fetch_event_data(self, event, year):
        try:
            event_data = (
                self.get_event_data(event, year),
                self.get_endgame_stats(event, year),
                self.get_penalties(event, year)
            )
            return event, event_data
        except Exception as e:
            print(f"Error fetching event data for {event}: {e}")
            return event, None

    def get_season(self, year=None, debug=False):
        year = year or self.find_year()
        events = self.get_season_events(year=year)
        season = Season(seasonCode=year)

        progress_bar = None
        if debug:
            progress_bar = tqdm(total=len(events), desc="Processing Events", unit=" event")

        max_threads = 400 
        with ThreadPoolExecutor(max_threads) as executor:
            futures = []
            for event in events:
                futures.append(executor.submit(self.fetch_event_data_thread, event, year, season, progress_bar))

            for future in futures:
                future.result()

        if progress_bar:
            progress_bar.close()

        return season

    def fetch_event_data_thread(self, event, year, season, progress_bar):
        event, eventData = self.fetch_event_data(event, year)
        if eventData:
            event_data = eventData[0]
            if event_data:
                season.events[event] = event_data.teams
        progress_bar.update(1)

    def get_event_data(self, eventCode, year=None):
        year = year or self.find_year()

        try:
            params = APIParams(path_segments=[year, 'matches', eventCode])
            response = self.client.api_request(params)
            match_data = response.get('matches', [])
        except Exception as e:
            print(f"Error fetching match data for event {eventCode}: {e}")
            return None

        try:
            endgame_stats, penalties = (
                self.get_endgame_stats(eventCode, year),
                self.get_penalties(eventCode, year)
            )
        except Exception as e:
            print(f"Error fetching additional data for event {eventCode}: {e}")
            return None

        modified_on_match_data = {}
        for match, endgame, penalty in zip(match_data, endgame_stats, penalties):
            match.update({
                "scoreRedEndgame": endgame["red"],
                "scoreBlueEndgame": endgame["blue"],
                "penaltyPointsRed": penalty["red"],
                "penaltyPointsBlue": penalty["blue"],
            })
            for team in match['teams']:
                team_number = team['teamNumber']
                modified_on_match_data.setdefault(team_number, match.get('modifiedOn', 'Unknown'))

        try:
            matrix_builder = MatrixBuilder(match_data)
            team_opr_values = {
                metric: mm.LSE(matrix_builder.binary_matrix, getattr(matrix_builder, f"{metric}_matrix"))
                for metric in ["auto", "tele", "endgame", "penalties"]
            }
        except Exception as e:
            print(f"Error building matrices for event {eventCode}: {e}")
            return None

        event = Event(eventCode=eventCode)
        for team in matrix_builder.teams:
            team_idx = matrix_builder.team_indices[team]

            try:
                team_info = self.get_team_info(team)
                team_info.teamNumber = team
                team_info.autoOPR = team_opr_values["auto"][team_idx]
                team_info.teleOPR = team_opr_values["tele"][team_idx]
                team_info.endgameOPR = team_opr_values["endgame"][team_idx]
                team_info.overallOPR = team_info.autoOPR + team_info.teleOPR
                team_info.penalties = team_opr_values["penalties"][team_idx]
                team_info.profileUpdate = modified_on_match_data.get(team, 'Unknown')
                event.teams.append(team_info)
            except Exception as e:
                print(f"Error processing team {team} for event {eventCode}: {e}")

        return event

    def get_endgame_stats(self, eventCode, year=None):
        year = year or self.find_year()
        params = APIParams(path_segments=[year, 'scores', eventCode, 'qual'])
        response = self.client.api_request(params)
        match_scores = response.get('matchScores', [])

        result = []
        for match in match_scores:
            red_alliance = match["alliances"][1]
            blue_alliance = match["alliances"][0]
            red_sum = red_alliance["teleopParkPoints"] + red_alliance["teleopAscentPoints"]
            blue_sum = blue_alliance["teleopParkPoints"] + blue_alliance["teleopAscentPoints"]
            result.append({"matchNumber": match["matchNumber"], "red": red_sum, "blue": blue_sum})

        return result

    def get_penalties(self, eventCode, year=None):
        year = year or self.find_year()
        params = APIParams(path_segments=[year, 'scores', eventCode, 'qual'])
        response = self.client.api_request(params)
        match_scores = response.get('matchScores', [])

        result = []
        for match in match_scores:
            red_alliance = match["alliances"][1]
            blue_alliance = match["alliances"][0]
            red_sum = red_alliance["foulPointsCommitted"]
            blue_sum = blue_alliance["foulPointsCommitted"]
            result.append({"matchNumber": match["matchNumber"], "red": red_sum, "blue": blue_sum})

        return result

    def get_team_info(self, team_number, year=None) -> Team:
        year = year or self.find_year()
        team_info_params = APIParams(
            path_segments=[year, 'teams'],
            query_params={'teamNumber': str(team_number)}
        )
        team_info = self.client.api_request(team_info_params)

        team_info = team_info.get('teams')[0]
        team_name = team_info.get('nameShort', "Unknown")
        sponsors = str(team_info.get('nameFull', "Unknown")).replace("/", ", ").replace("&", ", ").rstrip(", ")
        location = f"{team_info.get('city', 'Unknown')}, {team_info.get('stateProv', 'Unknown')}, {team_info.get('country', 'Unknown')}"
        
        return Team(
            teamName=team_name,
            sponsors=sponsors,
            location=location
        )

    @staticmethod
    def find_year():
        current_date = datetime.now()
        return current_date.year - 1 if current_date.month < 8 else current_date.year

def main():
    first_api = FirstAPI()
    season = first_api.get_season(year=2024, debug=True)
    print(f"Season Data: {season}")

if __name__ == "__main__":
    main()