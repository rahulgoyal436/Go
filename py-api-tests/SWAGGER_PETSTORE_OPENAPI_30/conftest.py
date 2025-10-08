import pytest
import requests
import yaml
from pathlib import Path
import os


# Fixture: Load configuration from config.yml
@pytest.fixture(scope="session")
def config():
    config_file = os.path.join(os.path.dirname(__file__), "config.yml")
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found at {config_file}")
    except yaml.YAMLError:
        pytest.fail("Error parsing YAML configuration file")


# Helper class for making API requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = os.path.join(self.base_url, endpoint.lstrip("/"))
        try:
            response = requests.request(method, url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed: {e}")

# Fixture: Provide an instance of APIHelper for making HTTP requests
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url)


# API Client for simpler operations like GET requests
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


# Fixture: Provide APIClient instance
@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Fixture: Extract valid API key from configuration
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Fixture: Provide a dummy invalid API key for testing
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY_12345"


# Fixture: Provide a test location parameter
@pytest.fixture(scope="session")
def valid_location():
    return "test-location"


# Fixture: Extract OAuth2 token from configuration
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]
