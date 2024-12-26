from dataclasses import dataclass,field
from typing import Dict
from .Team import Stats

@dataclass
class Alliance:
    team1: Stats
    team2: Stats
    color: str

    def __post_init__(self):
        self.alliance = self.team1 + self.team2

    def __str__(self):
        return (
            f"Alliance Color: {self.color}\n"
            f"Teams: {self.team1.teamNumber}, {self.team2.teamNumber}\n"
            f"Auto: {self.alliance.autoOPR}\n"
            f"TeleOp: {self.alliance.teleOPR}\n"
            f"Endgame: {self.alliance.endgameOPR}\n"
            f"Final Score: {self.alliance.overallOPR}"
        )
    def __repr__(self):
        return self.__str__()

@dataclass
class Match:
    redAlliance: Alliance
    blueAlliance: Alliance

    def __post_init__(self):
        self.winner = self.redAlliance if self.redAlliance.alliance.overallOPR > self.blueAlliance.alliance.overallOPR else self.blueAlliance

    def __str__(self):
        return (
            f"{self.redAlliance}\n"
            f"\n{self.blueAlliance}\n"
            f"Winner: {self.winner.color}"
        )
    def __repr__(self):
        return self.__str__()
    
@dataclass
class Event:
    """
    Stats for Tournament.

    Attributes:
        eventCode (str): The code for the event. Example: 'USAZTUQ'.
        teams (list[str]): A list of team numbers. Example: ['14584', '12345'].
        matches (Dict[str, Match]): A dictionary mapping match names to Match objects. Example: matches['Qualification 1'].
    """
    eventCode: str = None
    teams: list[str] = field(default_factory=list)
    matches: Dict[str,Match] = field(default_factory=dict)
