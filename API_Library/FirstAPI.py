import requests
from APIParams import APIParams
from API_Models.Team import Team

'''
Example usage(12/23/24):

newParams = APIParams('14584')
newOneCall = OneCallAPI(newParams)
team = newOneCall.get_team_data()
'''
class OneCallAPI:
    def __init__(self, params):
        if not isinstance(params, APIParams):
            raise TypeError('Incorrect type')
        
        self.base_url = "https://ftc-api.firstinspires.org/v2.0/2024/teams"
        self.username = 'hbono806'
        self.password = '5DC7537D-9DBB-463E-A11B-AAF25DD10B24'
        self.params = params

    def get_team_data(self):
        team_data = Team()
        
        params = {
            'teamNumber': self.params.teamNumber,
        }
        
        response = requests.get(self.base_url, auth=(self.username, self.password), params=params)
        
        if response.status_code == 200:
            team_data.set_team_name(response.json()['teams'][0]['nameShort'])
            team_data.set_location(response.json()['teams'][0]['city'] + ', ' + response.json()['teams'][0]['stateProv'] + ', ' + response.json()['teams'][0]['country'])
            team_data.set_sponsors(response.json()['teams'][0]['nameFull'])
            return team_data
        else:
            print(response.status_code)
            response.raise_for_status()
