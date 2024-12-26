import json
from operator import itemgetter
from tqdm import tqdm
from Response_Handler.API_Library.APIParams import APIParams
from Response_Handler.API_Library.FirstAPI import FirstAPI
from Response_Handler.FindData import FindData

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
        api_client = FirstAPI()
        event_codes = api_client.get_season_events(FindData.find_year())
        event_codes = ['USAZTUQ']
        
        for event in tqdm(event_codes, desc="Processing Tournaments", unit=" events"):
            matchOPRparams = APIParams([FindData.find_year(), 'matches', event])
            eventTourneyDict = FirstAPI().get_team_stats_from_tournament(matchOPRparams)

            for team in eventTourneyDict.teams:
                if team.teamNumber not in self.worldOPRTestDict:
                    self.worldOPRTestDict[team.teamNumber] = {
                        "teamNumber": team.teamNumber,
                        "autoOPR": team.autoOPR,
                        "teleOPR": team.teleOPR,
                        "endgameOPR": team.endgameOPR,
                        "overallOPR": team.overallOPR,
                        "modifiedOn": team.profileUpdate
                    }
                else:
                    if team.overallOPR > self.worldOPRTestDict[team.teamNumber]["overallOPR"]:
                        self.worldOPRTestDict[team.teamNumber] = {
                            "teamNumber": team.teamNumber,
                            "autoOPR": team.autoOPR,
                            "teleOPR": team.teleOPR,
                            "endgameOPR": team.endgameOPR,
                            "overallOPR": team.overallOPR,
                            "modifiedOn": team.profileUpdate
                        }
                    current_date = self.worldOPRTestDict[team.teamNumber]["modifiedOn"]
                    new_date = team.profileUpdate
                    if new_date > current_date:
                        self.worldOPRTestDict[team.teamNumber]["modifiedOn"] = new_date

        teams = list(self.worldOPRTestDict.values())

        auto_ranking = sorted(teams, key=itemgetter("autoOPR"), reverse=True)
        tele_ranking = sorted(teams, key=itemgetter("teleOPR"), reverse=True)
        endgame_ranking = sorted(teams, key=itemgetter("endgameOPR"), reverse=True)
        overall_ranking = sorted(teams, key=
                                 itemgetter("overallOPR"), reverse=True)

        for idx, team in enumerate(auto_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["autoRank"] = idx
        for idx, team in enumerate(tele_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["teleRank"] = idx
        for idx, team in enumerate(endgame_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["endgameRank"] = idx
        for idx, team in enumerate(overall_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["overallRank"] = idx
        with open(self.output_file, "w") as json_file:
            json.dump(self.worldOPRTestDict, json_file, indent=4)

        print(f"worldOPRTestDict has been saved to {self.output_file}")

worldcalc = WorldOPR()
worldcalc.calculate_world_opr_scores()