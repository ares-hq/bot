import os
import oracledb
from dotenv import load_dotenv
from API_Library.FirstAPI import FirstAPI
from API_Library.API_Models.Team import Team
from typing import Dict

# Attempting connection
try:
    import requests

    public_ip = requests.get("https://api4.ipify.org?format=text").text

    print("Public IP Address:", public_ip)
    print("Connecting to th database...")
    ceonn = oracledb.connect(
        user="ADMIN",
        password="Aquaticcanoe195!",
        dsn="(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.us-phoenix-1.oraclecloud.com))(connect_data=(service_name=gd1a25caa62f691_aresteamstorage_low.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))",
    )
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")

# Create table if it does not exist
with conn.cursor() as cursor:
    cursor.execute('''
    CREATE TABLE season_2024 (
        teamNumber NUMBER PRIMARY KEY,
        teamName VARCHAR2(255),
        sponsors VARCHAR2(1000),
        location VARCHAR2(500),
        autoOPR NUMBER,
        teleOPR NUMBER,
        endgameOPR NUMBER,
        overallOPR NUMBER,
        penalties NUMBER,
        profileUpdate TIMESTAMP,
        autoRank NUMBER,
        teleRank NUMBER,
        endgameRank NUMBER,
        overallRank NUMBER,
        penaltyRank NUMBER
    )''')
    conn.commit()

class TeamDataProcessor:
    def __init__(self):
        self.team_data: Dict[int, Team] = {}

    def fetch_season_data(self):
        first_api = FirstAPI()
        season = first_api.get_season(year=2024, debug=True)
        for event_data in season.events.values():
            for team in event_data:
                self.team_data[team.teamNumber] = team

    def save_to_database(self):
        with conn.cursor() as cursor:
            for team in self.team_data.values():
                cursor.execute('''
                MERGE INTO season_2024 t
                USING (SELECT :1 AS teamNumber FROM dual) d
                ON (t.teamNumber = d.teamNumber)
                WHEN MATCHED THEN UPDATE SET
                    teamName = :2, sponsors = :3, location = :4,
                    autoOPR = :5, teleOPR = :6, endgameOPR = :7,
                    overallOPR = :8, penalties = :9, profileUpdate = :10
                WHEN NOT MATCHED THEN INSERT (
                    teamNumber, teamName, sponsors, location, autoOPR,
                    teleOPR, endgameOPR, overallOPR, penalties, profileUpdate
                ) VALUES (
                    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10
                )''', (
                    team.teamNumber, team.teamName, team.sponsors,
                    team.location, team.autoOPR, team.teleOPR, team.endgameOPR,
                    team.overallOPR, team.penalties, team.profileUpdate
                ))
            conn.commit()

def main():
    processor = TeamDataProcessor()
    processor.fetch_season_data()
    processor.save_to_database()

if __name__ == "__main__":
    main()


# import os
# import logging
# from threading import Thread
# from dotenv import load_dotenv
# from tqdm import tqdm
# import libsql_experimental as sqlexp
# from API_Library.FirstAPI import FirstAPI
# from API_Library.API_Models.Team import Team
# from typing import Dict

# # Setup logging

# # Load environment variables
# load_dotenv()

# # Constants
# BATCH_SIZE = 100

# # Database connection setup
# url = os.getenv("TURSO_DATABASE_URL")
# auth_token = os.getenv("TURSO_AUTH_TOKEN")

# conn = sqlexp.connect("ares.db", sync_url=url, auth_token=auth_token)
# conn.sync()

# # Create the table if it doesn't exist
# conn.execute('''
# CREATE TABLE IF NOT EXISTS season_2024 (
#     teamNumber INTEGER PRIMARY KEY,
#     teamName TEXT,
#     sponsors TEXT,
#     location TEXT,
#     autoOPR REAL,
#     teleOPR REAL,
#     endgameOPR REAL,
#     overallOPR REAL,
#     penalties REAL,
#     profileUpdate TEXT,
#     autoRank INTEGER,
#     teleRank INTEGER,
#     endgameRank INTEGER,
#     overallRank INTEGER,
#     penaltyRank INTEGER
# )
# ''')

# class TeamDataProcessor:
#     def __init__(self):
#         self.team_data: Dict[int, Team] = {}

#     def fetch_season_data(self):
#         """
#         Fetch the data for the 2024 season from the API and populate the team data.
#         """
#         first_api = FirstAPI()
#         season = first_api.get_season(year=2024, debug=True)
#         logging.info("Season events fetched: %d", len(season.events))

#         # Process each event in the season
#         for event_id, event_data in season.events.items():
#             logging.info(f"Processing event {event_id}...")
#             for team_data in event_data:
#                 self._process_team_data(team_data)

#     def _process_team_data(self, team_data):
#         """
#         Process the team data and update the dictionary.
#         """
#         team_number = team_data.teamNumber
#         team_name = team_data.teamName
#         sponsors = team_data.sponsors
#         location = team_data.location
#         auto_opr = team_data.autoOPR
#         tele_opr = team_data.teleOPR
#         endgame_opr = team_data.endgameOPR
#         overall_opr = team_data.overallOPR
#         penalties = team_data.penalties
#         modified_on = team_data.profileUpdate

#         if team_number not in self.team_data:
#             # Add new team data
#             self.team_data[team_number] = Team(
#                 teamNumber=team_number,
#                 teamName=team_name,
#                 sponsors=sponsors,
#                 location=location,
#                 autoOPR=auto_opr,
#                 teleOPR=tele_opr,
#                 endgameOPR=endgame_opr,
#                 overallOPR=overall_opr,
#                 penalties=penalties,
#                 profileUpdate=modified_on,
#             )
#         else:
#             # Update existing team data if necessary
#             existing_team = self.team_data[team_number]
#             self._update_team_data(existing_team, team_data)

#     def _update_team_data(self, existing_team, team_data):
#         """
#         Update the team data if the new data is better or more recent.
#         """
#         if team_data.overallOPR > existing_team.overallOPR:
#             existing_team.autoOPR = team_data.autoOPR
#             existing_team.teleOPR = team_data.teleOPR
#             existing_team.endgameOPR = team_data.endgameOPR
#             existing_team.overallOPR = team_data.overallOPR
#             existing_team.penalties = team_data.penalties
        
#         if team_data.profileUpdate > existing_team.profileUpdate:
#             existing_team.profileUpdate = team_data.profileUpdate

#     def generate_rankings(self):
#         """
#         Rank the teams based on various OPR categories.
#         """
#         teams = list(self.team_data.values())
        
#         auto_ranking = sorted(teams, key=lambda t: t.autoOPR, reverse=True)
#         tele_ranking = sorted(teams, key=lambda t: t.teleOPR, reverse=True)
#         endgame_ranking = sorted(teams, key=lambda t: t.endgameOPR, reverse=True)
#         overall_ranking = sorted(teams, key=lambda t: t.overallOPR, reverse=True)
#         penalties_ranking = sorted(teams, key=lambda t: t.penalties)

#         self._assign_ranks(auto_ranking, 'autoRank')
#         self._assign_ranks(tele_ranking, 'teleRank')
#         self._assign_ranks(endgame_ranking, 'endgameRank')
#         self._assign_ranks(overall_ranking, 'overallRank')
#         self._assign_ranks(penalties_ranking, 'penaltyRank')

#     def _assign_ranks(self, ranking, rank_type):
#         """
#         Assign ranks to the teams based on the given ranking list.
#         """
#         for idx, team in enumerate(ranking, start=1):
#             setattr(team, rank_type, idx)

#     def save_to_database(self):
#         """
#         Save team data to the database using threading and batch processing.
#         """
#         teams_list = list(self.team_data.values())
#         chunks = [teams_list[i:i + BATCH_SIZE] for i in range(0, len(teams_list), BATCH_SIZE)]

#         threads = []
#         progress_bar = tqdm(total=len(teams_list), desc="Saving Team Data", unit=" team")

#         def process_chunk(chunk):
#             logging.debug(f"Processing chunk of size {len(chunk)}")
#             thread_conn = None
#             try:
#                 thread_conn = sqlexp.connect("ares.db", sync_url=url, auth_token=auth_token)
                
#                 for team in chunk:
#                     thread_conn.execute('''
#                         INSERT INTO season_2024 (
#                             teamNumber, teamName, sponsors, location, autoOPR, teleOPR, endgameOPR, overallOPR, 
#                             penalties, profileUpdate, autoRank, teleRank, endgameRank, overallRank, penaltyRank
#                         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                         ON CONFLICT(teamNumber) DO UPDATE SET
#                             teamName = excluded.teamName,
#                             sponsors = excluded.sponsors,
#                             location = excluded.location,
#                             autoOPR = excluded.autoOPR,
#                             teleOPR = excluded.teleOPR,
#                             endgameOPR = excluded.endgameOPR,
#                             overallOPR = excluded.overallOPR,
#                             penalties = excluded.penalties,
#                             profileUpdate = excluded.profileUpdate,
#                             autoRank = excluded.autoRank,
#                             teleRank = excluded.teleRank,
#                             endgameRank = excluded.endgameRank,
#                             overallRank = excluded.overallRank,
#                             penaltyRank = excluded.penaltyRank
#                     ''', (
#                         team.teamNumber, team.teamName, team.sponsors, team.location,
#                         team.autoOPR, team.teleOPR, team.endgameOPR, team.overallOPR,
#                         team.penalties, team.profileUpdate,
#                         team.autoRank, team.teleRank, team.endgameRank,
#                         team.overallRank, team.penaltyRank
#                     ))
                
#                 thread_conn.commit()
#                 progress_bar.update(len(chunk))
#             except Exception as e:
#                 logging.error(f"Error saving data: {e}")
#             finally:
#                 if thread_conn:
#                     thread_conn.close()

#         for chunk in chunks:
#             thread = Thread(target=process_chunk, args=(chunk,))
#             threads.append(thread)
#             thread.start()

#         for thread in threads:
#             thread.join()

#         progress_bar.close()

# def main():
#     data_processor = TeamDataProcessor()

#     # Step 1: Fetch season data
#     data_processor.fetch_season_data()

#     # Step 2: Generate rankings
#     data_processor.generate_rankings()

#     # Step 3: Save data to database
#     data_processor.save_to_database()

#     logging.info("Process completed successfully.")

# if __name__ == "__main__":
#     main()