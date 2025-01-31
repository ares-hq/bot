from dataclasses import dataclass, field

@dataclass
class Team:
    """
    Represents a robotics team with both performance statistics and profile information.

    Attributes:
        teamNumber (int): The team number.
        teamName (str): The name of the team.
        sponsors (str): The sponsors of the team.
        location (str): The location of the team.
        autoOPR (float): The autonomous OPR (Offensive Power Rating).
        teleOPR (float): The teleoperated OPR.
        endgameOPR (float): The endgame OPR.
        overallOPR (float): The overall OPR.
        autoRank (float): The rank in autonomous performance.
        teleRank (float): The rank in teleoperated performance.
        endgameRank (float): The rank in endgame performance.
        overallRank (float): The overall rank.
        penalties (float): The penalties incurred.
        penaltyRank (float): The rank based on penalties.
        profileUpdate (str): The last profile update timestamp.
    """
    teamNumber: int = field(default_factory=int)
    teamName: str = field(default_factory=str)
    sponsors: str = field(default_factory=str)
    location: str = field(default_factory=str)
    autoOPR: float = field(default_factory=float)
    teleOPR: float = field(default_factory=float)
    endgameOPR: float = field(default_factory=float)
    overallOPR: float = field(default_factory=float)
    autoRank: float = field(default_factory=float)
    teleRank: float = field(default_factory=float)
    endgameRank: float = field(default_factory=float)
    overallRank: float = field(default_factory=float)
    penalties: float = field(default_factory=float)
    penaltyRank: float = field(default_factory=float)
    profileUpdate: str = field(default_factory=str)

    def __post_init__(self):
        """Calculate overall OPR if not provided."""
        if self.overallOPR == 0:
            self.overallOPR = self.autoOPR + self.teleOPR + self.endgameOPR

    def __str__(self):
        """String representation of the team."""
        return (
            f"Team Number: {self.teamNumber}\n"
            f"Name: {self.teamName}\n"
            f"Sponsors: {self.sponsors}\n"
            f"Location: {self.location}\n"
            f"Auto OPR: {self.autoOPR:.2f} (Rank: {self.autoRank})\n"
            f"Tele OPR: {self.teleOPR:.2f} (Rank: {self.teleRank})\n"
            f"Endgame OPR: {self.endgameOPR:.2f} (Rank: {self.endgameRank})\n"
            f"Overall OPR: {self.overallOPR:.2f} (Rank: {self.overallRank})\n"
            f"Penalties OPR: {self.penalties:.2f} (Rank: {self.penaltyRank})\n"
            f"Last Updated: {self.profileUpdate}"
        )

    def update_profile(self, name: str = None, sponsors: str = None, location: str = None, timestamp: str = None):
        """
        Update the team's profile information.

        Args:
            name (str): New team name.
            sponsors (str): Updated sponsors.
            location (str): Updated location.
            timestamp (str): Timestamp of the update.
        """
        if name:
            self.teamName = name
        if sponsors:
            self.sponsors = sponsors
        if location:
            self.location = location
        if timestamp:
            self.profileUpdate = timestamp

    def add_stats(self, autoOPR: float = 0, teleOPR: float = 0, endgameOPR: float = 0, penalties: float = 0):
        """
        Add stats to the team's performance.

        Args:
            autoOPR (float): Additional autonomous OPR.
            teleOPR (float): Additional teleoperated OPR.
            endgameOPR (float): Additional endgame OPR.
            penalties (float): Additional penalties.
        """
        self.autoOPR += autoOPR
        self.teleOPR += teleOPR
        self.endgameOPR += endgameOPR
        self.penalties += penalties
        self.overallOPR = self.autoOPR + self.teleOPR + self.endgameOPR