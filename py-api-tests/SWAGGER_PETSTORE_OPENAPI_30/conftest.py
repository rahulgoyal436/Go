import pytest
import requests
import yaml
from pathlib import Path
import os


# Helper function to load YAML config
def load_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        pytest.fail(f"Config file not found at {config_path}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML file: {e}")


# Fixture to load configuration from config.yml
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    return load_config(config_path)


# Helper class for making API requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()


# Fixture for API helper
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url)


# Simple API client class using APIHelper
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


# Fixture for API client
@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Fixture to provide a valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Fixture to provide an invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"


# Fixture to provide a valid test location parameter
@pytest.fixture(scope="session")
def valid_location():
    return "New York, NY"


# Fixture to provide an OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"].get("petstore_auth")
