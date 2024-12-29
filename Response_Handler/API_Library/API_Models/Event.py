from dataclasses import dataclass,field
from typing import Dict
from . import Info,Stats,Summary

@dataclass
class Alliance:
    team1: Summary = field(default_factory=Summary)
    team2: Summary = field(default_factory=Summary)
    color: str = field(default_factory=str)

    def __post_init__(self):
        if not self.team1:
            self.team1 = Summary()
        if not self.team2:
            self.team2 = Summary()
        
        self.stats: Stats = self.team1.stats + self.team2.stats
        self.teamNums: list[int] = [self.team1.stats.teamNumber, self.team2.stats.teamNumber]
        self.teamNames: list[str] = [self.team1.info.teamName, self.team2.info.teamName]

        self.scoreboard:list[str] = [
            f"{self.teamNums[0]}",
            f"{self.teamNums[1]}",
            f"{self.stats.autoOPR:.0f}",
            f"{self.stats.teleOPR:.0f}",
            f"{self.stats.endgameOPR:.0f}",
            f"{self.stats.overallOPR:.0f}"
        ]

    counter = 0
    @classmethod # Default Alliance Color Given Blank Object
    def from_teams(cls, team1: Summary, team2: Summary):
        color = 'Red' if (cls.counter % 2 == 0) else 'Blue'
        cls.counter += 1
        return cls(team1=team1, team2=team2, color=color)


@dataclass
class Match:
    redAlliance: Alliance
    blueAlliance: Alliance
    winner: str = field(default_factory=str)

    def __post_init__(self):
        self.matchCategories = ["Team 1", "Team 2", "Autonomous", "TeleOp", "End Game", "Final Score"] # Designed to match "FIRST Tech Challenge" Competition Categories
        
        # Check if alliances are empty
        self.redAllianceEmpty = not self.redAlliance or not self.redAlliance.stats or all(value in [0, "", None] for value in self.redAlliance.stats.__dict__.values())
        self.blueAllianceEmpty = not self.blueAlliance or not self.blueAlliance.stats or all(value in [0, "", None] for value in self.blueAlliance.stats.__dict__.values())

       # Check if Either Alliance
        if not self.redAllianceEmpty and not self.blueAllianceEmpty and not self.winner:  # Alliance Winning Color Determined by Overall OPR
            if self.redAlliance.stats.overallOPR > self.blueAlliance.stats.overallOPR:
                self.winner = self.redAlliance.color
            elif self.redAlliance.stats.overallOPR < self.blueAlliance.stats.overallOPR:
                self.winner = self.blueAlliance.color
            else:
                self.winner = "Tie"
    
    def __str__(self):
        '''
        ASCII Table Representation of Match Object
        '''
         # Note: Max char limit for markdown rows is 55 characters

        table = "\rCategory      | Red Alliance | Blue Alliance\n"
        table += "--------------|--------------|--------------\n"
        for category, red_score, blue_score in zip(self.matchCategories, self.redAlliance.scoreboard, self.blueAlliance.scoreboard):
            table += f"{category:<14}| {red_score:<13}| {blue_score:<13}\n"
        table += f"Match Winner: {self.winner}\n\n" if self.winner not in ["", None] else None
        return table
        
        
@dataclass
class Event:
    """
    Stats for Tournament.

    Attributes:
        eventCode (str): The code for the event. Example: 'USAZTUQ'.
        teams (list[str]): A list of team numbers. Example: ['14584', '1234'].
        matches (Dict[str, Match]): A dictionary mapping match names to Match objects. Example: matches['Qualification 1'].
    """
    eventCode: str = field(default_factory=str)
    teams: list[str] = field(default_factory=list)
    matches: Dict[str,Match] = field(default_factory=dict)


# print(Match(Alliance(),Alliance()), Match(Alliance(),Alliance())) # Test Match Object
