import json
# from tqdm import tqdm
from dataclasses import dataclass,field
from Response_Handler.API_Library.APIParams import APIParams
from Response_Handler.API_Library.FirstAPI import FirstAPI
from Response_Handler.API_Library.API_Models.Season import History
from Response_Handler.API_Library.RobotMath.MatrixMath import MatrixMath as mm


'''
This class should only ever be run in the background. 
This class should never be called as a result from user message.
Upcoming: Implementation of world rankings.
'''
@dataclass
class WorldOPR:
    pass

@dataclass
class OPR:
    """
    This class is used to calculate the OPR for a team.

    Uses API and Matrix Algebra to calculate OPR per Event
    """
    method: function = mm.LSE
    teamNumber: int = None
    seasonCode: str = None

    def calculate_opr(self):
        pass

@dataclass
class Database:
    '''
    Stores Data for All Seasons Merged With Historical and Current OPR Data.
    
    History Object + World OPR Object (PER SEASON)
    
    '''
    history: History = None
    world_opr: WorldOPR = None

    # History + WorldOPR # Make add dunder method
    pass


