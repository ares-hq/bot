from dataclasses import dataclass,field
from typing import Dict
from .Team import Stats as ts

@dataclass
class Event:
    '''Stats for Tournament.'''
    teams: Dict[int, ts] = field(default_factory=dict)
    eventCode: str = ""

class Alliance:
    def __init__(self, team1: ts, team2: ts, color: str):
        self.team1 = team1
        self.team2 = team2
        self.color = color
        self.alliance = team1 + team2