from dataclasses import dataclass,field
from typing import Dict
from Team import Stats as ts

@dataclass
class Event:
    '''Stats for Tournament.'''
    teams: Dict[int, ts] = field(default_factory=dict)
    eventCode: str = ""
