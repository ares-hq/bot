from dataclasses import dataclass, field

@dataclass
class Info:
    """
    Profile info for team.

    Attributes:
        teamName (str): The name of the team.
        sponsors (str): The sponsors of the team.
        location (str): The location of the team.
    """
    teamName: str = field(default_factory=str)
    sponsors: str = field(default_factory=str)
    location: str = field(default_factory=str)

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
    teamNumber: int = field(default_factory=int)
    autoOPR: float = field(default_factory=float)
    teleOPR: float = field(default_factory=float)
    endgameOPR: float = field(default_factory=float)
    overallOPR: float = field(default_factory=float)
    autoRank: float = field(default_factory=float)
    penalties: float = field(default_factory=float)
    teleRank: float = field(default_factory=float)
    endgameRank: float = field(default_factory=float)
    overallRank: float = field(default_factory=float)
    profileUpdate: str = field(default_factory=str)

    def __post_init__(self):
        """
        Post-initialization processing to ensure that teamNumber is not None.
        """
        self.teamNumber = self.teamNumber or 0
        self.autoOPR = self.autoOPR or 0
        self.teleOPR = self.teleOPR or 0
        self.endgameOPR = self.endgameOPR or 0
        self.overallOPR = self.overallOPR or self.autoOPR + self.teleOPR + self.endgameOPR

        self._autoRank = self.autoRank
        self._teleRank = self.teleRank
        self._endgameRank = self.endgameRank
        self._overallRank = self.overallRank

    def __getattr__(self, name):
        """
        Example usage:
        
        >>> team = Stats(
        ...     teamNumber=1234,
        ...     autoOPR=10.5,
        ...     teleOPR=20.3,
        ...     endgameOPR=15.2,
        ...     overallOPR=46.0,
        ...     autoRank=1,
        ...     teleRank=2,
        ...     endgameRank=3,
        ...     overallRank=4,
        ...     profileUpdate="2023-10-01"
        ... )
        >>> print(team.autoRank)  # Output: 1st
        >>> print(team.teleRank)  # Output: 2nd
        >>> print(team.endgameRank)  # Output: 3rd
        >>> print(team.overallRank)  # Output: 4th
        """
        if name in ['autoRank', 'teleRank', 'endgameRank', 'overallRank']:
            rank = getattr(self, f"_{name}")
            if isinstance(rank, str) and rank[-2:] in ['st', 'nd', 'rd', 'th']:
                return rank
            if str(rank).endswith('3'):
                return str(rank) + 'rd'
            elif str(rank).endswith('2'):
                return str(rank) + 'nd'
            elif str(rank).endswith('1'):
                return str(rank) + 'st'
            else:
                return str(rank) + 'th'
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in ['autoRank', 'teleRank', 'endgameRank', 'overallRank']:
            super().__setattr__(f"_{name}", value)
        else:
            super().__setattr__(name, value)

    
    def __add__(self, other):
        """
        Adds two Stats objects or a Stats object and an Info object.

        Args:
            other (Stats or Info): The other object to add.

        Returns:
            Stats or Summary: The result of the addition.

        Raises:
            TypeError: If the other object is not a Stats or Info object.
        """
        if isinstance(other, Stats):
            return Stats(
                teamNumber= [self.teamNumber, other.teamNumber],
                autoOPR=    self.autoOPR + other.autoOPR,
                teleOPR=    self.teleOPR + other.teleOPR,
                endgameOPR= self.endgameOPR + other.endgameOPR,
                penalties= self.penalties + other.penalties,
                overallOPR= self.overallOPR + other.overallOPR
            )
        elif isinstance(other, Info):
            return Summary(info=other, stats=self)
        else:
            raise TypeError("Unsupported addition between Stats and non-Stats/Info object")
    
    def __str__(self):
        """
        Returns a string representation of the Stats object.
        """
        return (
            f"Team Number: **{self.teamNumber}**\n"
            f"Auto OPR: **{self.autoOPR:.2f}**\n"
            f"Auto Rank: **{self.autoRank}**\n"
            f"Tele OPR: **{self.teleOPR:.2f}**\n"
            f"Tele Rank: **{self.teleRank}**\n"
            f"Endgame OPR: **{self.endgameOPR:.2f}**\n"
            f"Endgame Rank: **{self.endgameRank}**\n"
            f"Commited Penalties OPR: **{self.penalties:.2f}**\n"
            f"Overall OPR: **{self.overallOPR:.2f}**\n"
            f"Overall Rank: **{self.overallRank}**\n"
        )
    
    def __repr__(self):
        """
        Returns a string representation of the Stats object for debugging.
        """
        return self.__str__()

@dataclass
class Summary:
    """
    Combines Info and Stats for a team.

    Attributes
    -----
        info (Info): The profile info for the team.
        stats (Stats): The match stats for the team.

    Example usage
    -----
        
        >>> info = Info(teamName="Team A", sponsors="Sponsor A", location="Location A", profileUpdate="2023-01-01")
        >>> stats = Stats(teamNumber=1234, autoOPR=10.0, teleOPR=20.0, endgameOPR=30.0, overallOPR=60.0)
        >>> summary = stats + info
        >>> print(summary)
        '''
        Team Name: Pioneer 327 (14584)
        Sponsors: Sponsor A
        Location: Location A
        Auto OPR: 10.0
        Tele OPR: 20.0
        Endgame OPR: 30.0
        Overall OPR: 60.0
        Profile Update: 2023-01-01
        '''

        >>> print(summary['info'])
        Info(teamName='Team A', sponsors='Sponsor A', location='Location A', profileUpdate='2023-01-01')

        >>> print(summary['stats'])
        Stats(teamNumber=1234, autoOPR=10.0, teleOPR=20.0, endgameOPR=30.0, overallOPR=60.0)
    """
    info: Info = field(default_factory=Info)
    stats: Stats = field(default_factory=Stats)

    def __post_init__(self):
        """
        Post-initialization processing to ensure that info attributes are not None.
        """
        self.info.teamName = self.info.teamName or ""
        self.info.sponsors = self.info.sponsors or ""
        self.info.location = self.info.location or ""
        self.stats.profileUpdate = self.stats.profileUpdate or ""

    def __getitem__(self, key):
        """
        Allows indexing to access info and stats attributes.
        """
        if key.lower() == 'info':
            return self.info
        elif key.lower() == 'stats':
            return self.stats
        else:
            raise KeyError(f"Key '{key}' not found in Summary")

    def __str__(self):
        """
        Returns a string representation of the Summary object.
        """
        return (
            f"Name: **{self.info.teamName}**\n"
            f"Sponsors: **{self.info.sponsors}**\n"
            f"Location: **{self.info.location}**\n"
            f"\n"
            f"Auto OPR: **{self.stats.autoOPR:.2f}** ({self.stats.autoRank})\n"
            f"Tele OPR: **{self.stats.teleOPR:.2f}** ({self.stats.teleRank})\n"
            f"Endgame OPR: **{self.stats.endgameOPR:.2f}** ({self.stats.endgameRank})\n"
            f"Penalties Committed OPR: **{self.stats.penalties:.2f}**\n"
            f"Overall OPR: **{self.stats.overallOPR:.2f}** ({self.stats.overallRank})\n"
            f"Last Updated: {self.stats.profileUpdate.replace("T", " ")}\n"
        )
