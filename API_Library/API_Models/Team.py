from dataclasses import dataclass, field

@dataclass
class Info:
    '''Profile info for team.'''
    teamName: str = field(default="")
    sponsors: str = field(default="")
    location: str = field(default="")
    profileUpdate: str = field(default="")

@dataclass
class Stats:
    '''Match stats for team.'''
    teamNumber: int = field(default=0)
    autoOPR: float = field(default=0.0)
    teleOPR: float = field(default=0.0)
    endgameOPR: float = field(default=0.0)
    overallOPR: float = field(default=0.0)