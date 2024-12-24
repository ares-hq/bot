"""
This module provides utility functions and a class for handling API parameters related to a specific team.

Functions:
- get_current_season: Determines the current season based on the current date.
- get_event_date_range: Calculates a date range around the current date.

Classes:
- APIParams: A class to manage API parameters for a specific team.

The APIParams class includes:
- __init__: Initializes the class with a team number.
"""
class APIParams:
    def __init__(self, teamNumber, apiStringList):
        self.teamNumber = teamNumber
        self.apiStringList = apiStringList