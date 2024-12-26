import json
from tqdm import tqdm
from Response_Handler.API_Library.APIParams import APIParams
from Response_Handler.API_Library.FirstAPI import FirstAPI

'''
This class should only ever be run in the background. 
This class should never be called as a result from user message.
Upcoming: Implementation of world rankings.
'''
class WorldOPR:
    def __init__(self):
        self.worldOPRTestDict = {}
        self.output_file = "world_opr_scores_.json"

    def calculate_world_opr_scores(self):
        event_code_params = APIParams(
            path_segments=[FirstAPI.find_year(), 'events']
        )

        api_client = FirstAPI()
        event_codes = api_client.get_season_events(event_code_params)
        
        for event in tqdm(event_codes, desc="Processing Tournaments", unit="events"):
            matchOPRparams = APIParams('',[FirstAPI.findYear(), 'matches', event])
            eventTourneyDict = FirstAPI(matchOPRparams).get_team_stats().tournament_dict
            
            for team, stats in eventTourneyDict.items():        
                if team not in self.worldOPRTestDict:
                    self.worldOPRTestDict[team] = stats
                else:
                    if stats["Overall OPR"] > self.worldOPRTestDict[team]["Overall OPR"]:
                        self.worldOPRTestDict[team] = stats
        with open(self.output_file, "w") as json_file:
            json.dump(self.worldOPRTestDict, json_file, indent=4)

        print(f"worldOPRTestDict has been saved to {self.output_file}")