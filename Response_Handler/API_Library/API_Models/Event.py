from dataclasses import dataclass,field
from typing import Dict
from .Team import Stats,Info,Summary

@dataclass
class Alliance:
    team1: Summary
    team2: Summary
    color: str

    def __post_init__(self):
        self.alliance: Stats = self.team1['stats'] + self.team2['stats']

    def __str__(self):
        ''' Red ASCII = \033[31m .... \033[0m \n
            Blue ASCII = \033[34m .... \033[0m \n
            White ASCII = \033[7m .... \033[0m 
            '''
        return (
                "```markdown\n"
                "**Teams**\n"
                f"{self.team1.stats.teamNumber}\n"
                f"{self.team2.stats.teamNumber}\n"
                "\n"
                "**Auto**\n"
                f"{self.alliance.autoOPR:.0f}\n"
                "**Teleop**\n"
                f"{self.alliance.teleOPR:.0f}\n"
                "**Endgame**\n"
                f"{self.alliance.endgameOPR:.0f}\n"
                "\n"
                "**Score**\n"
                f"{self.alliance.overallOPR:.0f}\n"
                "```"
        )

@dataclass
class Match:
    redAlliance: Alliance
    blueAlliance: Alliance

    def __post_init__(self):
        self.redScores: Stats = self.redAlliance.alliance
        self.blueScores: Stats = self.blueAlliance.alliance
        self.winner = self.redAlliance if self.redScores.overallOPR > self.blueScores.overallOPR else self.blueAlliance

    def __str__(self):
        return (
                                                "| **Red Alliance**        || **Blue Alliance**      |\n"
                                                "|-------------------------||-------------------------|\n"
            f"| **Team1**: {self.redAlliance.team1.stats.teamNumber}        || **Team1**: {self.blueAlliance.team1.stats.teamNumber}         |\n"
            f"| **Team2**: {self.redAlliance.team2.stats.teamNumber}        || **Team2**: {self.blueAlliance.team2.stats.teamNumber}          |\n"
            f"| **Auto**: {self.redScores.autoOPR:.2f}                     || **Auto**: {self.blueScores.autoOPR:.2f}          |\n"
            f"| **Teleop**: {self.redScores.teleOPR:.2f}                   || **Teleop**: {self.blueScores.teleOPR:.2f}        |\n"
            f"| **Endgame**: {self.redScores.endgameOPR:.2f}               || **Endgame**: {self.blueScores.endgameOPR:.2f}       |\n"
            f"| **Score**: {self.redScores.overallOPR:.2f}                 || **Score**: {self.blueScores.overallOPR:.2f}         |"
            "\n"
            f"**Winner**: {self.winner.color} Alliance"
        )
    
@dataclass
class Event:
    """
    Stats for Tournament.

    Attributes:
        eventCode (str): The code for the event. Example: 'USAZTUQ'.
        teams (list[str]): A list of team numbers. Example: ['14584', '1234'].
        matches (Dict[str, Match]): A dictionary mapping match names to Match objects. Example: matches['Qualification 1'].
    """
    eventCode: str = None
    teams: list[str] = field(default_factory=list)
    matches: Dict[str,Match] = field(default_factory=dict)
