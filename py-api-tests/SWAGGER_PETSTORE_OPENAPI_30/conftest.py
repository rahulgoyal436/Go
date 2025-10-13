import pytest
import requests
import yaml
from pathlib import Path
import os


@pytest.fixture(scope="session")
def config():
    """Load configuration from config.yml file."""
    try:
        config_path = Path(os.path.dirname(__file__)).joinpath("config.yml")
        with open(config_path, "r") as file:
            configuration = yaml.safe_load(file)
        return configuration
    except FileNotFoundError:
        pytest.exit("config.yml not found!")
    except yaml.YAMLError as e:
        pytest.exit(f"Error parsing config.yml: {e}")


class ApiHelper:
    """Helper class for making HTTP requests."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        method = method.upper()

        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return response
        except requests.RequestException as e:
            pytest.fail(f"HTTP request failed: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture for API helper."""
    base_url = config["api"]["host"].strip()
    return ApiHelper(base_url)


class ApiClient:
    """Simple API client for making HTTP GET requests."""
    
    def __init__(self, helper):
        self.helper = helper

    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture for API client."""
    return ApiClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture to provide a valid API key."""
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture to provide an invalid API key."""
    return "invalid-api-key"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture to provide a test location for requests."""
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture to provide an OAuth2 token."""
    return config["authentication"]["petstore_auth"]
