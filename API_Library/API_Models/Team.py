class Team:
    def __init__(self):
        self.teamName = None
        self.sponsors = None
        self.location = None
        self.profileUpdate = None

    def get_team_name(self):
        '''
        Gets the team name.
        '''
        return self.teamName

    def set_team_name(self, teamName):
        self.teamName = teamName

    def get_sponsors(self):
        '''
        Gets the team sponsors.
        '''
        return self.sponsors

    def set_sponsors(self, sponsors):
        self.sponsors = sponsors

    def get_location(self):
        '''
        Gets the team City, State/Provence, Country.
        '''
        return self.location

    def set_location(self, location):
        self.location = location
        
    def get_profile_update(self):
        '''
        Gets the profile update timestamp.
        '''
        return self.profileUpdate

    def set_profile_update(self, profileUpdate):
        self.profileUpdate = profileUpdate