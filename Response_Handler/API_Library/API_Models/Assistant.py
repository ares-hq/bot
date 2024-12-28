import requests
from . import Event, Team, Season, Stats, Summary, Alliance, Match, History


'''
Class is  just Pseudo Code for now
GOAL: Move @FirstAPI methods to Assistant
'''

class Assistant:

    @staticmethod
    def filter_events_by_date(events, start_date, end_date):
        return [event for event in events if start_date <= event['date'] <= end_date]

    @staticmethod
    def get_team_names(teams):
        return [team['name'] for team in teams]

    @staticmethod
    def get_event_team_names(event_id):
        teams = Assistant.get_event_teams(event_id)
        return Assistant.get_team_names(teams)

    @staticmethod
    def get_season_event_names(season_id):
        events = Assistant.get_season_events(season_id)
        return [event['name'] for event in events]

    @staticmethod
    def get_team_event_names(team_id):
        events = Assistant.get_team_events(team_id)
        return [event['name'] for event in events]

    @staticmethod
    def get_team_season_stats(history: History, team_number: int):
        team_stats = {}
        for season_code, season in history.Seasons.items():
            season_stats = {
                'totalOPR': 0,
                'numAwards': 0,
                'tournamentAppearances': 0
            }
            for event_code, event in season.events.items():
                if team_number in event.teams:
                    season_stats['tournamentAppearances'] += 1
                    for match in event.matches.values():
                        if team_number in [match.redAlliance.team1.stats.teamNumber, match.redAlliance.team2.stats.teamNumber]:
                            season_stats['totalOPR'] += match.redScores.overallOPR
                        elif team_number in [match.blueAlliance.team1.stats.teamNumber, match.blueAlliance.team2.stats.teamNumber]:
                            season_stats['totalOPR'] += match.blueScores.overallOPR
            team_stats[season_code] = season_stats
        return team_stats

    @staticmethod
    def get_team_awards(history: History, team_number: int):
        team_awards = {}
        for season_code, season in history.Seasons.items():
            awards = 0
            for event_code, event in season.events.items():
                if team_number in event.teams:
                    awards += event.numAwarded
            team_awards[season_code] = awards
        return team_awards

    @staticmethod
    def get_team_season_summary(history: History, team_number: int):
        summary = {}
        for season_code, season in history.Seasons.items():
            season_summary = {
                'totalOPR': 0,
                'numAwards': 0,
                'tournamentAppearances': 0
            }
            for event_code, event in season.events.items():
                if team_number in event.teams:
                    season_summary['tournamentAppearances'] += 1
                    season_summary['numAwards'] += event.numAwarded
                    for match in event.matches.values():
                        if team_number in [match.redAlliance.team1.stats.teamNumber, match.redAlliance.team2.stats.teamNumber]:
                            season_summary['totalOPR'] += match.redScores.overallOPR
                        elif team_number in [match.blueAlliance.team1.stats.teamNumber, match.blueAlliance.team2.stats.teamNumber]:
                            season_summary['totalOPR'] += match.blueScores.overallOPR
            summary[season_code] = season_summary
        return summary