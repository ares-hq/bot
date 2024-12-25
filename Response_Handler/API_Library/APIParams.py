class APIParams:
    """
    Modular and flexible API parameters class.
    """
    def __init__(self, path_segments=None, query_params=None):
        """
        Initialize API parameters.
        :param path_segments: (list) List of URL path segments.
        :param query_params: (dict) Dictionary of query parameters for the API call.
        """
        self.path_segments = path_segments or []
        self.query_params = query_params or {}

    def to_path_segments(self):
        """
        Return the path segments for URL construction.
        """
        return [segment for segment in self.path_segments if segment]

    def to_query_params(self):
        """
        Return the query parameters for the API request.
        """
        return self.query_params