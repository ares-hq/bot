import numpy as np

class MatrixBuilder():
    def __init__(self, matches):
        self.matches = matches
        self.teams = []
        self.num_matches = len(matches)
        self.num_teams = 0
        self.binary_matrix = None
        self.auto_matrix = np.zeros((self.num_matches * 2), dtype=int)
        self.tele_matrix = np.zeros((self.num_matches * 2), dtype=int)
        self.endgame_matrix = np.zeros((self.num_matches * 2), dtype=int)
        self.penalties_matrix = np.zeros((self.num_matches * 2), dtype=int)
        self.team_indices = None
        
        self.create_binary_and_score_matrices()
        
    def create_team_matrices(self):
        '''This function is neccesary to find all teams in a given tournament.'''
        
        for match in self.matches:
            for team in match['teams']:
                if team['teamNumber'] not in self.teams:
                    self.teams.append(team['teamNumber'])
            
        self.team_indices = {team: idx for idx, team in enumerate(self.teams)}
        self.num_teams = len(self.teams)
        self.binary_matrix = np.zeros((self.num_matches * 2, self.num_teams), dtype=int)
        
    def create_binary_and_score_matrices(self):
        '''This function creates the binary and score matrices based on the team alliance scores in a given tournament.'''
        
        # Make sure to init team matrices before creating binary and score matrices
        self.create_team_matrices()
        
        for match_idx, match in enumerate(self.matches):
            red_score = match.get('scoreRedFinal', 0) - match.get('scoreRedAuto', 0) - match.get('scoreBlueFoul', 0)
            blue_score = match.get('scoreBlueFinal', 0) - match.get('scoreBlueAuto', 0) - match.get('scoreRedFoul', 0)
            red_score_auto = match.get('scoreRedAuto', 0)
            blue_score_auto = match.get('scoreBlueAuto', 0)
            red_score_endgame = match.get('scoreRedEndgame', 0)
            blue_score_endgame = match.get('scoreBlueEndgame', 0)
            red_score_penalties = match.get('penaltyPointsRed', 0)
            blue_score_penalties = match.get('penaltyPointsBlue', 0)
            
            for team in match['teams']:
                team_idx = self.team_indices[team['teamNumber']]
                station = str(team['station'])
                
                '''
                This calls 'onField', which checks to see if a team is on the field during this match.
                However, this is not used in normal OPR calculations so it is subject to change.
                '''
                if 'Qualification' in match['description'] and team['onField']:
                    if "Red" in station:
                        self.binary_matrix[2*match_idx, team_idx] = 1
                    elif "Blue" in station:
                        self.binary_matrix[2*match_idx + 1, team_idx] = 1 

            self.tele_matrix[2 * match_idx] = red_score
            self.tele_matrix[2 * match_idx + 1] = blue_score
            self.auto_matrix[2 * match_idx] = red_score_auto
            self.auto_matrix[2 * match_idx + 1] = blue_score_auto
            self.endgame_matrix[2 * match_idx] = red_score_endgame
            self.endgame_matrix[2 * match_idx + 1] = blue_score_endgame
            self.penalties_matrix[2 * match_idx] = red_score_penalties
            self.penalties_matrix[2 * match_idx + 1] = blue_score_penalties            