import pytest
import requests
import yaml
from pathlib import Path
import os

# Load configuration fixture
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        pytest.fail(f"Config file not found at {config_path}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing config file: {e}")

# Helper class for handling HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method=method, url=url, params=params, headers=headers
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            pytest.fail(f"Request failed: {e}")

# Fixture to provide API helper
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        pytest.fail("API base URL is not defined in config")
    return APIHelper(base_url=base_url)

# Simple API client built on top of APIHelper
class APIClient:
    def __init__(self, helper):
        self.helper = helper

    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method="GET")

# Fixture to provide API client
@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)

# Fixture to provide a valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key")
    if not api_key:
        pytest.fail("Valid API key is not defined in config")
    return api_key

# Fixture to provide an invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"

# Fixture to provide a valid test location
@pytest.fixture(scope="session")
def valid_location():
    return "test-location"

# Fixture to provide OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth")
    if not token:
        pytest.fail("OAuth2 token is not defined in config")
    return token
