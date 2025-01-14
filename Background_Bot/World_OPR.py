import asyncio
import concurrent.futures
import json
from operator import itemgetter
from tqdm import tqdm
from Response_Handler.API_Library.FirstAPI import FirstAPI
from Response_Handler.API_Library.APIParams import APIParams
from Response_Handler.FindData import FindData

class WorldOPR:
    def __init__(self):
        self.worldOPRTestDict = {}
        self.output_file = "world_opr_scores_.json"
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def fetch_event_data_sync(self, event, api_client):
        """
        Fetch event data synchronously for a given event code.
        """
        matchOPRparams = APIParams([FindData.find_year(), 'matches', event])
        return api_client.get_team_stats_from_tournament(matchOPRparams)

    async def fetch_event_data(self, event, api_client):
        """
        Wrap the synchronous method to be used asynchronously.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.fetch_event_data_sync, event, api_client)

    async def process_event(self, event, api_client):
        """
        Process the data for a single event, updating the world OPR dictionary.
        """
        try:
            eventTourneyDict = await self.fetch_event_data(event, api_client)

            for team in eventTourneyDict.teams:
                if team.teamNumber not in self.worldOPRTestDict:
                    self.worldOPRTestDict[team.teamNumber] = {
                        "teamNumber": team.teamNumber,
                        "autoOPR": team.autoOPR,
                        "teleOPR": team.teleOPR,
                        "endgameOPR": team.endgameOPR,
                        "overallOPR": team.overallOPR,
                        "penalties": team.penalties,
                        "modifiedOn": team.profileUpdate,
                    }
                else:
                    if team.overallOPR > self.worldOPRTestDict[team.teamNumber]["overallOPR"]:
                        self.worldOPRTestDict[team.teamNumber].update({
                            "autoOPR": team.autoOPR,
                            "teleOPR": team.teleOPR,
                            "endgameOPR": team.endgameOPR,
                            "overallOPR": team.overallOPR,
                            "penalties": team.penalties,
                        })
                    if team.profileUpdate > self.worldOPRTestDict[team.teamNumber]["modifiedOn"]:
                        self.worldOPRTestDict[team.teamNumber]["modifiedOn"] = team.profileUpdate
        except Exception as e:
            print(f"Error processing event {event}: {e}")

    async def calculate_world_opr_scores(self):
        """
        Main function to calculate world OPR scores for all events.
        """
        api_client = FirstAPI()
        event_codes = api_client.get_season_events(FindData.find_year())

        # Use tqdm in a synchronous manner
        progress_bar = tqdm(total=len(event_codes), desc="Processing Tournaments", unit=" events")

        async def task_wrapper(event):
            await self.process_event(event, api_client)
            progress_bar.update(1)

        tasks = [task_wrapper(event) for event in event_codes]
        await asyncio.gather(*tasks)
        progress_bar.close()

        # Create rankings
        teams = list(self.worldOPRTestDict.values())

        auto_ranking = sorted(teams, key=itemgetter("autoOPR"), reverse=True)
        tele_ranking = sorted(teams, key=itemgetter("teleOPR"), reverse=True)
        endgame_ranking = sorted(teams, key=itemgetter("endgameOPR"), reverse=True)
        overall_ranking = sorted(teams, key=itemgetter("overallOPR"), reverse=True)

        for idx, team in enumerate(auto_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["autoRank"] = idx
        for idx, team in enumerate(tele_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["teleRank"] = idx
        for idx, team in enumerate(endgame_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["endgameRank"] = idx
        for idx, team in enumerate(overall_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["overallRank"] = idx

        # Save the results
        with open(self.output_file, "w") as json_file:
            json.dump(self.worldOPRTestDict, json_file, indent=4)

        print(f"worldOPRTestDict has been saved to {self.output_file}")


if __name__ == "__main__":
    worldcalc = WorldOPR()
    asyncio.run(worldcalc.calculate_world_opr_scores())