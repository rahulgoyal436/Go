import pytest
import requests
import yaml
from pathlib import Path
import os


# Fixture to load configuration from config.yml file
@pytest.fixture(scope="session")
def config():
    config_path = Path(os.path.join(os.path.dirname(__file__), "config.yml"))
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with open(config_path, "r") as file:
        try:
            config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error reading YAML config file: {e}")
    return config_data


# Helper class for making HTTP requests
class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
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
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")


# Fixture to provide an instance of ApiHelper
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("Base URL is not defined in the configuration file.")
    return ApiHelper(base_url)


# Simple API client using ApiHelper
class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


# Fixture to provide an instance of ApiClient
@pytest.fixture(scope="session")
def api_client(api_helper):
    return ApiClient(api_helper)


# Fixture to extract a valid API key from the configuration
@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key", "").strip()
    if not api_key:
        raise ValueError("Valid API key is not defined in the configuration file.")
    return api_key


# Fixture to provide a dummy invalid API key for testing
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"


# Fixture to provide a test location parameter
@pytest.fixture(scope="session")
def valid_location():
    return {"location": "TestLocation"}


# Fixture to extract OAuth2 token from the configuration
@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth", "").strip()
    if not token:
        raise ValueError("OAuth2 token is not defined in the configuration file.")
    return token
