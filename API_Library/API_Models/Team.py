class Info:
    '''Profile info for team.'''
    def __init__(self):
        self._teamName = None
        self._sponsors = None
        self._location = None
        self._profileUpdate = None

    @property
    def teamName(self):
        '''
        Gets the team name.
        '''
        return self._teamName

    @teamName.setter
    def teamName(self, value):
        '''
        Sets the team name.
        '''
        self._teamName = value

    @property
    def sponsors(self):
        '''
        Gets the team sponsors.
        '''
        return self._sponsors

    @sponsors.setter
    def sponsors(self, value):
        '''
        Sets the team sponsors.
        '''
        self._sponsors = value

    @property
    def location(self):
        '''
        Gets the team City, State/Province, Country.
        '''
        return self._location

    @location.setter
    def location(self, value):
        '''
        Sets the team City, State/Province, Country.
        '''
        self._location = value

    @property
    def profileUpdate(self):
        '''
        Gets the profile update timestamp.
        '''
        return self._profileUpdate

    @profileUpdate.setter
    def profileUpdate(self, value):
        '''
        Sets the profile update timestamp.
        '''
        self._profileUpdate = value

class Stats:
    '''Stats for team.'''
    def __init__(self):
        self._autoOPR = None
        self._teleOPR = None
        self._endgameOPR = None
        self._overallOPR = None

    @property
    def autoOPR(self):
        '''
        Gets the team auto OPR (Offensive Power Rating).
        '''
        return self._autoOPR

    @autoOPR.setter
    def autoOPR(self, value):
        '''
        Sets the team auto OPR (Offensive Power Rating).
        '''
        self._autoOPR = value

    @property
    def teleOPR(self):
        '''
        Gets the teleoperated OPR (Offensive Power Rating).
        '''
        return self._teleOPR

    @teleOPR.setter
    def teleOPR(self, value):
        '''
        Sets the teleoperated OPR (Offensive Power Rating).
        '''
        self._teleOPR = value

    @property
    def endgameOPR(self):
        '''
        Gets the endgame OPR (Offensive Power Rating).
        '''
        return self._endgameOPR

    @endgameOPR.setter
    def endgameOPR(self, value):
        '''
        Sets the endgame OPR (Offensive Power Rating).
        '''
        self._endgameOPR = value

    @property
    def overallOPR(self):
        '''
        Gets the overall OPR (Offensive Power Rating).
        '''
        return self._overallOPR

    @overallOPR.setter
    def overallOPR(self, value):
        '''
        Sets the overall OPR (Offensive Power Rating).
        '''
        self._overallOPR = value