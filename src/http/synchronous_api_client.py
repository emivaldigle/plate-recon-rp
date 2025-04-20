import requests
import logging
import json
from requests.auth import HTTPBasicAuth

class SynchronousAPIClient:
    def __init__(self, base_url, username="root", password="root"):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password)
        self.logger = logging.getLogger(__name__)

    def log_request(self, method, url, headers, params=None, data=None):
        self.logger.info(f"Request -> {method} {url}")
        if headers:
            self.logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        if params:
            self.logger.info(f"Params: {json.dumps(params, indent=2)}")
        if data:
            self.logger.info(f"Payload: {json.dumps(data, indent=2)}")

    def log_response(self, response):
        self.logger.info(f"Response <- {response.status_code}")
        try:
            self.logger.info(f"Body: {json.dumps(response.json(), indent=2)}")
        except json.JSONDecodeError:
            self.logger.info(f"Raw Response: {response.text}")

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        full_headers = headers or {}
        self.log_request("GET", url, full_headers, params)
        response = requests.get(url, params=params, headers=full_headers, auth=self.auth)
        self.log_response(response)
        response.raise_for_status()  
        return response.json()

    def post(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        full_headers = headers or {}
        payload = json if json else data
        self.log_request("POST", url, full_headers, data=payload)
        response = requests.post(url, data=data, json=json, headers=full_headers, auth=self.auth)
        self.log_response(response)
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        full_headers = headers or {}
        payload = json if json else data
        self.log_request("PATCH", url, full_headers, data=payload)
        response = requests.patch(url, data=data, json=json, headers=full_headers, auth=self.auth)
        self.log_response(response)
        response.raise_for_status()
        return response.json()
