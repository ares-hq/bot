from dataclasses import dataclass

@dataclass
class Info:
    """
    Profile info for team.

    Attributes:
        teamName (str): The name of the team.
        sponsors (str): The sponsors of the team.
        location (str): The location of the team.
        profileUpdate (str): The date of the last profile update.
    """
    teamName: str = None
    sponsors: str = None
    location: str = None
    profileUpdate: str = None

@dataclass
class Stats:
    """
    Match stats for team.

    Attributes:
        teamNumber (int): The team number.
        autoOPR (float): The autonomous OPR (Offensive Power Rating).
        teleOPR (float): The teleoperated OPR.
        endgameOPR (float): The endgame OPR.
        overallOPR (float): The overall OPR.
    """
    teamNumber: int = None
    autoOPR: float = None
    teleOPR: float = None
    endgameOPR: float = None
    overallOPR: float = None
    
    def __add__(self, other):
        return Stats(
            teamNumber=[self.teamNumber, other.teamNumber],
            autoOPR=self.autoOPR + other.autoOPR,
            teleOPR=self.teleOPR + other.teleOPR,
            endgameOPR=self.endgameOPR + other.endgameOPR,
            overallOPR=self.overallOPR + other.overallOPR
        )
    