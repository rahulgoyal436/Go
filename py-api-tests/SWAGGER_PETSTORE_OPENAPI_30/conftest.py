import pytest
import yaml
import os
import requests
from pathlib import Path

class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Error making request: {e}")

class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

@pytest.fixture(scope="session")
def config():
    config_path = Path(os.path.join(os.path.dirname(__file__), "config.yml"))
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error loading configuration file: {e}")

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("API base URL is missing in the configuration file")
    return APIHelper(base_url)

@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)

@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key", "").strip()
    if not api_key:
        raise ValueError("Valid API key is missing in the configuration file")
    return api_key

@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_dummy_api_key"

@pytest.fixture(scope="session")
def valid_location():
    return {"lat": 40.7128, "lng": -74.0060}  # Example test location (e.g., New York City)

@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth", "").strip()
    if not token:
        raise ValueError("OAuth2 token is missing in the configuration file")
    return token
