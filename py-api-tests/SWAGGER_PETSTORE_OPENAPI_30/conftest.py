import pytest
import requests
import yaml
import os
from pathlib import Path

# Fixture to load the configuration from config.yml
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"The configuration file at {config_path} does not exist.")
    
    try:
        with config_path.open("r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error reading the configuration YAML file: {e}")

# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        params = params or {}
        headers = headers or {}

        if method == "GET":
            response = requests.get(url, params=params, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=params, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=params, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        return response

# Fixture to provide the API helper instance
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("API host URL is not properly configured in the config.yml file.")
    return APIHelper(base_url)

# Fixture for a simple API client
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")

@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)

# Fixture to provide a valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("valid_api_key")
    if not api_key:
        raise ValueError("Valid API key is missing from the config.yml file.")
    return api_key

# Fixture to provide an invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"

# Fixture to provide a test location parameter
@pytest.fixture(scope="session")
def valid_location():
    return {"location": "test-location"}

# Fixture to provide an OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("oauth2_token")
    if not token:
        raise ValueError("OAuth2 token is missing from the config.yml file.")
    return token
