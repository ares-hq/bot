# class APIParams:
#     """
#     Modular and flexible API parameters class.
#     """
#     def __init__(self, path_segments=None, query_params=None):
#         """
#         Initialize API parameters.
#         :param path_segments: (list) List of URL path segments.
#         :param query_params: (dict) Dictionary of query parameters for the API call.
#         """
#         self.path_segments = path_segments or []
#         self.query_params = query_params or {}

#     def to_path_segments(self):
#         """
#         Return the path segments for URL construction.
#         """
#         return [segment for segment in self.path_segments if segment]

#     def to_query_params(self):
#         """
#         Return the query parameters for the API request.
#         """
#         return self.query_params
    
class APIParams:
    """
    A versatile and reusable class to manage API parameters.
    """
    def __init__(self, path_segments=None, query_params=None):
        """
        Initialize API parameters.
        :param path_segments: (list) List of URL path segments.
        :param query_params: (dict) Dictionary of query parameters for the API call.
        """
        self.path_segments = path_segments or []
        self.query_params = query_params or {}

    def add_path_segment(self, segment):
        """
        Add a single path segment.
        :param segment: (str) Path segment to add.
        """
        if segment:
            self.path_segments.append(segment)

    def add_query_param(self, key, value):
        """
        Add a single query parameter.
        :param key: (str) Query parameter key.
        :param value: Query parameter value.
        """
        if key and value is not None:
            self.query_params[key] = value

    def to_path_segments(self):
        """
        Return a list of path segments for URL construction.
        :return: (list) List of valid path segments.
        """
        return [str(segment) for segment in self.path_segments if segment]

    def to_query_params(self):
        """
        Return the query parameters as a dictionary.
        :return: (dict) Query parameters.
        """
        return self.query_params