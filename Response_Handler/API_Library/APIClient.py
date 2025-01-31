import os
import requests
from dotenv import load_dotenv

class APIClient:
    """
    A simple and flexible API client for making requests.
    """
    def __init__(self, base_url):
        """
        Initialize the API client.
        :param base_url: (str) The base URL of the API.
        """
        load_dotenv()
        self.base_url = base_url.rstrip('/')
        self.username = os.getenv('FIRST_USERNAME')
        self.password = os.getenv('FIRST_PASS')

        if not self.username or not self.password:
            raise EnvironmentError("Environment variables API_USERNAME and API_PASSWORD are required.")

        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    def build_url(self, apiParams):
        """
        Build a URL using the base URL, path segments, and optional query parameters.
        :param path_segments: (list) List of path segments.
        :param params: (dict, optional) Query parameters for the URL.
        :return: (str) Constructed URL.
        """
        # Join the path segments to form the URL path
        path = "/".join(str(segment) for segment in apiParams.path_segments if segment)

        # Initialize the URL
        url = f"{self.base_url}/{path}"

        # If params are provided, format them into `key=value` pairs
        if apiParams.query_params:
            query_string = "&".join(f"{key}={value}" for key, value in apiParams.query_params.items())
            url = f"{url}?{query_string}"

        return url
    
    def api_request(self, api_params, params=None, headers=None):
        """
        Make a GET request to the API.
        :param path_segments: (list) Path segments for the URL.
        :param params: (dict) Query parameters for the request.
        :param headers: (dict) Additional headers for the request.
        :return: (dict) JSON response from the API.
        """
        url = self.build_url(api_params)
        response = self.session.get(url, params=params, headers=headers)

        if not response.ok:
            response.raise_for_status()

        return response.json()
    
    def post_request(self, path_segments, data=None, headers=None):
        """
        Make a POST request to the API.
        :param path_segments: (list) Path segments for the URL.
        :param data: (dict) Data to send in the POST request.
        :param headers: (dict) Additional headers for the request.
        :return: (dict) JSON response from the API.
        """
        url = self.build_url(path_segments)
        response = self.session.post(url, json=data, headers=headers)

        if not response.ok:
            response.raise_for_status()

        return response.json()

    def get_last_update(self):
        """
        Get the last update time from the API.
        :return: (str) Last update timestamp.
        """
        response = self.api_request(['last_update'])
        return response.get('lastUpdate')