from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import Client, create_client

from Response_Handler.API_Models import Team

class SupabaseHandler:
    def __init__(self, supabase_url=None, supabase_key=None):
        if not supabase_url or not supabase_key:
            load_dotenv()
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            if not supabase_url or not supabase_key:
                raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.table = "season_2024"
        self.team_data = {}

    def get_response(self, team_number, table_name="null"):
        """
        Fetches data from the Supabase table based on the provided query.

        Args:
            table_name (str): The name of the table to query.
            query (dict): The query parameters.

        Returns:
            list: A list of records matching the query.
        """
        if table_name == "null":
            table_name = f"season{self.find_year()}"
        if table_name not in self.team_data:
            self.team_data[table_name] = {}

            raw_data = self.supabase.table(self.table).select("*").execute().data or []
            for row in raw_data:
                tnum = row.get("teamNumber")
                if tnum is not None:
                    self.team_data[table_name][tnum] = Team(
                        teamName=row["teamName"],
                        sponsors=row["sponsors"],
                        location=row["location"],
                        teamNumber=tnum,
                        autoOPR=row["autoOPR"],
                        teleOPR=row["teleOPR"],
                        endgameOPR=row["endgameOPR"],
                        overallOPR=row["overallOPR"],
                        penalties=row["penalties"],
                        autoRank=row.get("autoRank"),
                        teleRank=row.get("teleRank"),
                        endgameRank=row.get("endgameRank"),
                        overallRank=row.get("overallRank"),
                        penaltyRank=row.get("penaltyRank"),
                        profileUpdate=row.get("profileUpdate"),
                        eventDate=row.get("eventDate"),
                    )

        return self.team_data[table_name].get(team_number, Team())
    
    @staticmethod     
    def find_year():
        current_date = datetime.now()
        return current_date.year - 1 if current_date.month < 8 else current_date.year

# SupabaseHandler = SupabaseHandler()
# print(SupabaseHandler.get_response(14584))