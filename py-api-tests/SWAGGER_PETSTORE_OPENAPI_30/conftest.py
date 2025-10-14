import pytest
import requests
import yaml
import os
from pathlib import Path


@pytest.fixture(scope="session")
def config():
    """Load configuration from the config.yml file."""
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as exc:
        pytest.fail(f"Error reading configuration file: {exc}")


class APIHelper:
    """Helper class for making HTTP requests."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method=method, url=url, params=params, headers=headers)
            return response
        except requests.RequestException as e:
            pytest.fail(f"Request failed: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Provide an instance of APIHelper with the base URL."""
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        pytest.fail("API base URL not found in configuration.")
    return APIHelper(base_url)


class APIClient:
    """Simple API client for making HTTP GET requests."""

    def __init__(self, helper):
        self.helper = helper

    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, method="GET", headers=headers, params=params)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide an instance of APIClient."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract valid API key from configuration."""
    return config.get("authentication", {}).get("api_key", "").strip()


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide a dummy invalid API key."""
    return "invalid-api-key-for-testing"


@pytest.fixture(scope="session")
def valid_location():
    """Provide a test location parameter."""
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from configuration."""
    return config.get("authentication", {}).get("petstore_auth", "").strip()
