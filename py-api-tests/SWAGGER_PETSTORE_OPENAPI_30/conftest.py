import pytest
import requests
import yaml
from pathlib import Path
import os


@pytest.fixture(scope="session")
def config():
    """
    Load configuration from config.yml file.
    """
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            conf = yaml.safe_load(file)
            return conf
    except FileNotFoundError:
        pytest.fail("Configuration file 'config.yml' not found.")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing configuration file: {e}")


@pytest.fixture(scope="session")
def api_helper():
    """
    Helper class for making HTTP requests.
    """
    class APIHelper:
        def __init__(self, base_url):
            self.base_url = base_url.rstrip("/")

        def make_request(self, endpoint, params=None, headers=None, method="GET"):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.request(method, url, params=params, headers=headers)
            return response

    return APIHelper


@pytest.fixture(scope="session")
def api_client(config, api_helper):
    """
    API client with simple methods for GET requests.
    """
    class APIClient:
        def __init__(self, helper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            return self.helper.make_request(endpoint, params=params, headers=headers, method="GET")

    base_url = config["api"]["host"]
    return APIClient(api_helper(base_url))


@pytest.fixture(scope="session")
def valid_api_key(config):
    """
    Extract valid API key from the configuration file.
    """
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    """
    Provide a dummy invalid API key for testing.
    """
    return "invalid-api-key"


@pytest.fixture(scope="session")
def valid_location():
    """
    Provide a sample valid test location parameter.
    """
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """
    Extract OAuth2 token from the configuration file.
    """
    return config["authentication"]["petstore_auth"]
