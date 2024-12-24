import requests
import scipy
from APIParams import APIParams
from API_Models.Team import Info as ti, Stats as ts
import os
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
from RobotMath.MatrixMath import LSE

'''
Example usage(12/23/24):

newParams = APIParams('14584')
newOneCall = FirstAPI(newParams)
team = newOneCall.get_team_data()
'''
class FirstAPI:
    def __init__(self, params):
        if not isinstance(params, APIParams):
            raise TypeError('Incorrect type')
        load_dotenv()
        
        self.params = params
        self.base_url = "https://ftc-api.firstinspires.org/v2.0"
        self.template = f"{self.base_url}/{'/'.join(map(str, self.params.apiStringList))}" if self.params.apiStringList else self.base_url
        self.username = os.getenv('FIRST_USERNAME')
        self.password = os.getenv('FIRST_PASS')

    def get_team_info(self):
        team_data = ti()
                
        response = self.api_request({
            'teamNumber': self.params.teamNumber,
        })
        
        if response.status_code == 200:
            team_data.teamName = response.json()['teams'][0]['nameShort']
            team_data.location = response.json()['teams'][0]['city'] + ', ' + response.json()['teams'][0]['stateProv'] + ', ' + response.json()['teams'][0]['country']
            team_data.sponsors = response.json()['teams'][0]['nameFull']
            return team_data
        else:
            print(response.status_code)
            response.raise_for_status()
            
    def get_team_stats(self):
        team_stats = ts()
        team_number_index = []
        alliance_partners_matrix = []
        alliance_partner_scores = []

        response = self.api_request({}) 

        if response.status_code == 200:
            response = response.json()
            
            # Extract teams
            all_teams = []
            for match in response['matches']:
                for team in match['teams']:
                    # print(team['teamNumber'])
                    if team['teamNumber'] not in all_teams:
                        all_teams.append(team['teamNumber'])
            # all_teams = sorted(list(all_teams))  # Sort for consistent column order
            
            # Create team indices for the matrix
            team_indices = {team: idx for idx, team in enumerate(all_teams)}

            # Initialize matrices
            num_matches = len(response['matches'])
            num_teams = len(all_teams)
            
            num_matches = len(response['matches'])
            num_teams = len(all_teams)

            # Each match will have two rows: one for Red alliance and one for Blue alliance
            binary_matrix = np.zeros((num_matches * 2, num_teams), dtype=int)

            # Score matrix will have two rows per match (one for Red and one for Blue alliance)
            score_matrix = np.zeros((num_matches * 2), dtype=int)  # One column for each alliance score

            binary_matrix = np.zeros((num_matches*2, num_teams), dtype=int)
            score_matrix = np.zeros((num_matches*2), dtype=int)  # Columns: [Red Score, Blue Score]
            
            # Populate matrices
            for match_idx, match in enumerate(response['matches']):
                # Initialize red and blue scores for the current match
                red_score = match.get('scoreRedFinal', 0)
                blue_score = match.get('scoreBlueFinal', 0)
                red_score_penalty = match.get('scoreRedFoul', 0)
                blue_score_penalty = match.get('scoreBlueFoul', 0)
                
                for team in match['teams']:
                    team_idx = team_indices[team['teamNumber']]
                    station = str(team['station'])
                    
                    # Check if the team is on the Red or Blue alliance
                    if "Red" in station and team['onField']:
                        binary_matrix[2*match_idx, team_idx] = 1  # Red team
                    elif "Blue" in station and team['onField']:
                        binary_matrix[2*match_idx + 1, team_idx] = 1  # Blue team

                    # (Optional) Extract auto, teleop, or endgame scores here
                    # Example: auto_scores[match_idx, team_idx] = team.get('autoScore', 0)
                
                # Populate score matrix: separate rows for Red and Blue alliances
                score_matrix[2 * match_idx] = red_score #- red_score_penalty  # Red score
                score_matrix[2 * match_idx + 1] = blue_score #- blue_score_penalty  # Blue score

            # # Print results
            # print("Binary Matrix (Team Appearances):")
            print(binary_matrix[1])

            # print("\nScore Matrix (Red and Blue Scores):")
            print(score_matrix[1])
            # print(all_teams)
            
            # team_stats.autoOPR = response.json()['teams'][0]['nameShort']
            # team_stats.teleOPR = response.json()['teams'][0]['city'] + ', ' + response.json()['teams'][0]['stateProv'] + ', ' + response.json()['teams'][0]['country']
            # team_stats.endgameOPR = response.json()['teams'][0]['nameFull']
            
            team_stats.overallOPR = LSE(matrixA=binary_matrix, matrixB=score_matrix).getLeastSquares()
            teamScoreDict = {}
            i = 0
            for x in all_teams:
                teamScoreDict[x] = team_stats.overallOPR[i]
                i += 1
            return teamScoreDict
        else:
            print(response.status_code)
            response.raise_for_status() 
    
    def get_season_events(self):
        response = self.api_request({}) # Use base URL
        
        if response.status_code == 200:
            codes = [event["code"] for event in response.json()["events"]]
            return codes
    
    def api_request(self, params):
        return requests.get(self.template, auth=(self.username, self.password), params=params)
    
    def findYear():
        current_date = datetime.now()

        if current_date.month < 8:
            season_year = current_date.year - 1
        else:
            season_year = current_date.year
            
        return season_year

teamInfoParams = APIParams('14584', [FirstAPI.findYear(), 'teams'])
eventCodeParams = APIParams('',[FirstAPI.findYear(), 'events'])
matchOPRparams = APIParams('',[FirstAPI.findYear(), 'matches', 'USAZTUQ'])

newOneCall = FirstAPI(matchOPRparams)
# team = newOneCall.get_team_data()
# print(team.location)

codes = newOneCall.get_team_stats()
print(codes)