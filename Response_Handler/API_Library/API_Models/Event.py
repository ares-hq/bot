from dataclasses import dataclass,field
from typing import Dict
from .Team import Stats,Info,Summary

@dataclass
class Alliance:
    team1: Summary = field(default_factory=Summary)
    team2: Summary = field(default_factory=Summary)
    color: str = field(default_factory=str)


    @classmethod
    def from_teams(cls, team1: Summary, team2: Summary):
        color = 'red' if (cls.counter % 2 == 0) else 'blue'
        cls.counter += 1
        return cls(team1=team1, team2=team2, color=color)

    counter = 0

    def __post_init__(self):
        if not self.team1:
            self.team1 = Summary()
        if not self.team2:
            self.team2 = Summary()
        self.alliance: Stats = self.team1.stats + self.team2.stats

@dataclass
class Match:
    redAlliance: Alliance
    blueAlliance: Alliance

    def __post_init__(self):
        self.redScores: Stats = self.redAlliance.alliance
        self.blueScores: Stats = self.blueAlliance.alliance
        if self.redScores.overallOPR > self.blueScores.overallOPR:
            self.winner = self.redAlliance.color
        elif self.redScores.overallOPR < self.blueScores.overallOPR:
            self.winner = self.blueAlliance.color
        else:
            self.winner = "Tie"

    def __str__(self):
        categories = ["Team 1", "Team 2", "Auto", "TeleOp", "End Game", "Final Score", "Winner"]
        red_scores = [
            str(self.redScores.teamNumber[0]),
            str(self.redScores.teamNumber[1]),
            f"{self.redScores.autoOPR:.0f}",
            f"{self.redScores.teleOPR:.0f}",
            f"{self.redScores.endgameOPR:.0f}",
            f"{self.redScores.overallOPR:.0f}"
        ]
        blue_scores = [
            str(self.blueScores.teamNumber[0]),
            str(self.blueScores.teamNumber[1]),
            f"{self.blueScores.autoOPR:.0f}",
            f"{self.blueScores.teleOPR:.0f}",
            f"{self.blueScores.endgameOPR:.0f}",
            f"{self.blueScores.overallOPR:.0f}"
        ]

        red_formatted =  '\n'.join(f"- {score}" for score in red_scores)
        blue_formatted = '\n'.join(f"[{score}]" for score in blue_scores)

        if self.winner == "Tie":
            winner_text = "```fix\nTie\n```"
        else:
            winner_text = f"```diff\n- {self.winner}\n```" if self.winner == 'Red' else f"```ini\n[ {self.winner} ]\n```"

        return [
            f"{'\n'.join(categories)}",
            f"```diff\n{red_formatted}\n```",
            f"\n```ini\n{blue_formatted}\n```",
            f"{winner_text}"
        ]
        
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
