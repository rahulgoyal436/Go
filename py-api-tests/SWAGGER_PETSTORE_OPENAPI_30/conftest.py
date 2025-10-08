import pytest
import requests
import yaml
from pathlib import Path

# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=params)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=params)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, json=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response.json()

# Simple API Client
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, headers=headers, params=params, method='GET')

@pytest.fixture(scope="session")
def config():
    config_path = Path("config.yml")
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    with config_path.open("r") as file:
        try:
            config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration file: {e}")
    return config_data

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("API host URL is missing in the configuration file.")
    return APIHelper(base_url)

@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)

@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key")
    if not api_key:
        raise ValueError("Valid API key is missing in the configuration file.")
    return api_key

@pytest.fixture(scope="session")
def invalid_api_key():
    return "this_is_an_invalid_api_key"

@pytest.fixture(scope="session")
def valid_location():
    return {"lat": 37.7749, "lon": -122.4194}  # Example coordinates for San Francisco

@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth")
    if not token:
        raise ValueError("OAuth2 token is missing in the configuration file.")
    return token
