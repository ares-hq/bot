import libsql_experimental as libsql
import os
from dotenv import load_dotenv
import asyncio
import concurrent.futures
from operator import itemgetter
from tqdm import tqdm
from Response_Handler.API_Library.FirstAPI import FirstAPI
from Response_Handler.API_Library.APIParams import APIParams
from Response_Handler.FindData import FindData

# Load environment variables from .env file
load_dotenv()

# Fetch database URL and auth token from environment variables
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

# Connect to the Turso database
conn = libsql.connect("ares.db", sync_url=url, auth_token=auth_token)
conn.sync()
conn.set_log_output(None)

# Create the opr_scores table if it doesn't exist
conn.execute('''
CREATE TABLE IF NOT EXISTS opr_scores (
    teamNumber INTEGER PRIMARY KEY,
    autoOPR REAL,
    teleOPR REAL,
    endgameOPR REAL,
    overallOPR REAL,
    penalties REAL,
    modifiedOn TEXT,
    autoRank INTEGER,
    teleRank INTEGER,
    endgameRank INTEGER,
    overallRank INTEGER,
    penaltiesRank INTEGER
)
''')

# Class to calculate and save OPR data
class WorldOPR:
    def __init__(self):
        self.worldOPRTestDict = {}
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
        penalties_ranking = sorted(teams, key=itemgetter("penalties"))

        for idx, team in enumerate(auto_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["autoRank"] = idx
        for idx, team in enumerate(tele_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["teleRank"] = idx
        for idx, team in enumerate(endgame_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["endgameRank"] = idx
        for idx, team in enumerate(overall_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["overallRank"] = idx
        for idx, team in enumerate(penalties_ranking, start=1):
            self.worldOPRTestDict[team["teamNumber"]]["penaltiesRank"] = idx

        # Save results to Turso database incrementally with progress bar
        teams_list = list(self.worldOPRTestDict.values())
        progress_bar = tqdm(total=len(teams_list), desc="Saving Team Data", unit=" team")
        
        for team in teams_list:
            try:
                conn.execute('''
                    INSERT INTO opr_scores (
                        teamNumber, autoOPR, teleOPR, endgameOPR, overallOPR, penalties, modifiedOn,
                        autoRank, teleRank, endgameRank, overallRank, penaltiesRank
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(teamNumber) DO UPDATE SET
                        autoOPR = excluded.autoOPR,
                        teleOPR = excluded.teleOPR,
                        endgameOPR = excluded.endgameOPR,
                        overallOPR = excluded.overallOPR,
                        penalties = excluded.penalties,
                        modifiedOn = excluded.modifiedOn,
                        autoRank = excluded.autoRank,
                        teleRank = excluded.teleRank,
                        endgameRank = excluded.endgameRank,
                        overallRank = excluded.overallRank,
                        penaltiesRank = excluded.penaltiesRank
                ''', (
                    team["teamNumber"], team["autoOPR"], team["teleOPR"], team["endgameOPR"], 
                    team["overallOPR"], team["penalties"], team["modifiedOn"],
                    team["autoRank"], team["teleRank"], team["endgameRank"], 
                    team["overallRank"], team["penaltiesRank"]
                ))

                # Commit after each insertion to ensure data is saved incrementally
                conn.commit()
                progress_bar.update(1)  # Update progress bar for each insertion
            except Exception as e:
                print(f"Error saving data for team {team['teamNumber']}: {e}")

        progress_bar.close()  # Close progress bar after all teams have been saved

    def close_connection(self):
        conn.close()

if __name__ == "__main__":
    worldcalc = WorldOPR()
    try:
        asyncio.run(worldcalc.calculate_world_opr_scores())
    finally:
        worldcalc.close_connection()