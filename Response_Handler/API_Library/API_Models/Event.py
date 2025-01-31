from dataclasses import dataclass, field
from typing import Dict, List
from .Team import Team

@dataclass
class Alliance:
    team1: Team = field(default_factory=Team)
    team2: Team = field(default_factory=Team)
    color: str = field(default_factory=str)
    combined_autoOPR: float = 0.0
    combined_teleOPR: float = 0.0
    combined_endgameOPR: float = 0.0
    combined_penalties: float = 0.0
    combined_overallOPR: float = 0.0

    def __post_init__(self):
        self.combined_autoOPR = self.team1.autoOPR + self.team2.autoOPR
        self.combined_teleOPR = self.team1.teleOPR + self.team2.teleOPR
        self.combined_endgameOPR = self.team1.endgameOPR + self.team2.endgameOPR
        self.combined_penalties = self.team1.penalties + self.team2.penalties
        self.combined_overallOPR = self.combined_autoOPR + self.combined_teleOPR + self.combined_endgameOPR

        self.teamNums: List[int] = [self.team1.teamNumber, self.team2.teamNumber]
        self.teamNames: List[str] = [self.team1.teamName, self.team2.teamName]

        self.scoreboard: List[str] = [
            f"{self.teamNums[0]}",
            f"{self.teamNums[1]}",
            f"{self.combined_autoOPR:.0f}",
            f"{self.combined_teleOPR:.0f}",
            f"{self.combined_endgameOPR:.0f}",
            f"{self.combined_penalties:.0f}",
            f"{self.combined_overallOPR:.0f}"
        ]

@dataclass
class Match:
    redAlliance: Alliance
    blueAlliance: Alliance
    winner: str = field(default_factory=str)

    def __post_init__(self):
        self.matchCategories = [
            "Team 1", "Team 2", "Autonomous", "TeleOp", "End Game", "Penalties", "Final Score"
        ]

        self.redAllianceEmpty = all(
            value in [0, "", None] for value in [
                self.redAlliance.combined_autoOPR,
                self.redAlliance.combined_teleOPR,
                self.redAlliance.combined_endgameOPR,
                self.redAlliance.combined_penalties,
                self.redAlliance.combined_overallOPR
            ]
        )
        self.blueAllianceEmpty = all(
            value in [0, "", None] for value in [
                self.blueAlliance.combined_autoOPR,
                self.blueAlliance.combined_teleOPR,
                self.blueAlliance.combined_endgameOPR,
                self.blueAlliance.combined_penalties,
                self.blueAlliance.combined_overallOPR
            ]
        )

        if not self.redAllianceEmpty and not self.blueAllianceEmpty and not self.winner:
            if self.redAlliance.combined_overallOPR > self.blueAlliance.combined_overallOPR:
                self.winner = self.redAlliance.color
            elif self.redAlliance.combined_overallOPR < self.blueAlliance.combined_overallOPR:
                self.winner = self.blueAlliance.color
            else:
                self.winner = "Tie"

    def __str__(self):
        """ASCII Table Representation of Match Object."""
        table = "\rCategory      | Red Alliance | Blue Alliance\n"
        table += "--------------|--------------|--------------\n"
        for category, red_score, blue_score in zip(
            self.matchCategories, self.redAlliance.scoreboard, self.blueAlliance.scoreboard
        ):
            table += f"{category:<14}| {red_score:<13}| {blue_score:<13}\n"
        if self.winner:
            table += f"Match Winner: {self.winner}\n"
        return table

@dataclass
class Event:
    eventCode: str = field(default_factory=str)
    teams: List[Team] = field(default_factory=list)
    matches: Dict[str, Match] = field(default_factory=dict)