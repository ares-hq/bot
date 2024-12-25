from FindData import FindData

class HandleMessageResponse():
    '''
    Example Usage
    -----
    
    messageHandler = HandleMessageResponse() \n
    newdict = messageHandler.match_message_data([1454, 284], [1454, 284]) \n
    '''
    def __init__(self):
        self.data_search = FindData()
    
    def team_message_data(self, teamNumber):
        '''
        Returns a dictionary containing the data neccesary for the team message.
        {
            'message': {string message if team exists or not}
            'Team Name': String, 
            'Auto OPR': Float, 
            'TeleOp OPR': Float, 
            'Overall OPR': Float, 
            'Sponsors': String, 
            'Location': String
        }
        '''
        team_stats = self.data_search.find_team_stats_from_json(teamNumber)
        team_info = self.data_search.callForTeamInfo(teamNumber)
        try:
            if team_info is not None:
                team_dict = {
                    'message': 'Query OK',
                    'Team Name':team_info.teamName,
                    'Auto OPR':team_stats.autoOPR,
                    'TeleOp OPR':team_stats.teleOPR,
                    'Overall OPR':team_stats.overallOPR,
                    'Sponsors':team_info.sponsors,
                    'Location':team_info.location
                }
            else:
                team_dict = {
                    'message': 'No data found for this team.'
                }
        except Exception as e:
            return TypeError("Team not found.")
        
        return team_dict
    
    def match_message_data(self, redAlliance, blueAlliance=None):
        '''
        Returns a dictionary containing the data neccesary for the match message.
        {
            'Estimated Winner': {Red or Blue Alliance}
            {Red or Blue Alliance}: {
                'message': {string message if team exists or not}
                'Auto OPR': Float, 
                'TeleOp OPR': Float, 
                'Estimated Score': Float, 
                'Team Names': List
                {team number}:{
                    'message': 'Query OK',
                    'Team Name':team_info.teamName,
                    'Auto OPR':team_stats.autoOPR,
                    'TeleOp OPR':team_stats.teleOPR,
                    'Overall OPR':team_stats.overallOPR,
                    'Sponsors':team_info.sponsors,
                    'Location':team_info.location
                }
            }
        }
        '''
        match_dict = {}
        red_alliance = {
            'Auto OPR':0.0,
            'TeleOp OPR':0.0,
            'Estimated Score':0.0,
            'Team Names':[]
        }
        blue_alliance = {
            'Auto OPR':0.0,
            'TeleOp OPR':0.0,
            'Estimated Score':0.0,
            'Team Names':[]
        }
        
        for team in redAlliance:
            team_dict = self.team_message_data(team)
            red_alliance[team] = team_dict
            try:
                red_alliance["Auto OPR"] += team_dict['Auto OPR']
                red_alliance["TeleOp OPR"] += team_dict['TeleOp OPR']
                red_alliance["Estimated Score"] += team_dict['Overall OPR']
                red_alliance['Team Names'].append(team_dict['Team Name'])   
            except TypeError as e:
                return TypeError(f"Team {team} not found.")
            match_dict['Red Alliance'] = red_alliance 

        if blueAlliance:
            for team in blueAlliance:
                team_dict = self.team_message_data(team)
                blue_alliance[team] = team_dict
                try:                    
                    blue_alliance["Auto OPR"] += team_dict['Auto OPR']
                    blue_alliance["TeleOp OPR"] += team_dict['TeleOp OPR']
                    blue_alliance["Estimated Score"] += team_dict['Overall OPR']
                    blue_alliance['Team Names'].append(team_dict['Team Name']) 
                except TypeError as e:
                    return TypeError(f"Team {team} not found.")
                match_dict['Blue Alliance'] = blue_alliance
     
            match_dict['Estimated Winner'] = 'Red Alliance' if red_alliance['Estimated Score'] > blue_alliance['Estimated Score'] else 'Blue Alliance'

        return match_dict

messageHandler = HandleMessageResponse()
newdict = messageHandler.match_message_data([14584, 14584])
print(newdict['Red Alliance'])