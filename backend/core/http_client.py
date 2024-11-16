import requests


class HTTPClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, params=None, headers=None):
        url = self.base_url + endpoint
        response = requests.get(url, params=params, headers=headers)
        return response

    def post(self, endpoint, data=None, headers=None):
        url = self.base_url + endpoint
        response = requests.post(url, json=data, headers=headers)
        return response

    # Add other HTTP methods as needed (e.g., put, delete, etc.)
    # Example:
    def put(self, endpoint, data=None, headers=None):
        url = self.base_url + endpoint
        response = requests.put(url, json=data, headers=headers)
        return response
