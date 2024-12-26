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
    autoRank: float = None
    teleRank: float = None
    endgameRank: float = None
    overallRank: float = None
    profileUpdate: str = None
    
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
                teamNumber=[self.teamNumber, other.teamNumber],
                autoOPR=self.autoOPR + other.autoOPR,
                teleOPR=self.teleOPR + other.teleOPR,
                endgameOPR=self.endgameOPR + other.endgameOPR,
                overallOPR=self.overallOPR + other.overallOPR,
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
            f"Overall OPR: **{self.overallOPR:.2f}**\n"
            f"Overall Rank: **{self.overallRank}**\n"
        )
    
    def __repr__(self):
        """
        Returns a string representation of the Stats object for debugging.
        """
        return self.__str__()
    
    def __post_init__(self):
        self.autoRank = self.add_suffix(self.autoRank)
        self.teleRank = self.add_suffix(self.teleRank)
        self.endgameRank = self.add_suffix(self.endgameRank)
        self.overallRank = self.add_suffix(self.overallRank)

    def add_suffix(self, rank):
        if str(rank).endswith('3'):
            return str(rank) + 'rd'
        elif str(rank).endswith('2'):
            return str(rank) + 'nd'
        elif str(rank).endswith('1'):
            return str(rank) + 'st'
        else:
            return str(rank) + 'th'

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
    info: Info
    stats: Stats

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
            f"Location: **{self.info.location}**\n \n"
            f"Auto OPR: **{self.stats.autoOPR:.2f} ({self.stats.autoRank})**\n"
            f"Tele OPR: **{self.stats.teleOPR:.2f} ({self.stats.teleRank})**\n"
            f"Endgame OPR: **{self.stats.endgameOPR:.2f} ({self.stats.endgameRank})**\n"
            f"Overall OPR: **{self.stats.overallOPR:.2f} ({self.stats.overallRank})**\n"
            f"\n*Last Updated:* ***{self.stats.profileUpdate.replace("T", " ")}***"
        )
    
    def __repr__(self):
        """
        Returns a string representation of the Summary object for debugging.
        """
        return self.__str__()