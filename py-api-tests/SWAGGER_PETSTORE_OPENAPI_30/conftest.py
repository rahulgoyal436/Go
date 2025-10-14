import os
import pytest
import requests
import yaml
from pathlib import Path


@pytest.fixture(scope="session")
def config():
    """
    Fixture to load the YAML configuration file.
    """
    config_path = Path(__file__).parent / "config.yml"

    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")

    with config_path.open("r") as file:
        try:
            config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing the configuration file: {e}")

    return config_data


class APIHelper:
    """
    Helper class for making HTTP requests.
    """
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        method = method.upper()

        if method not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
            raise ValueError(f"Unsupported HTTP method: {method}")

        try:
            response = requests.request(method, url, headers=headers, params=params)
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """
    Fixture to provide an APIHelper instance.
    """
    base_url = config["api"]["host"].strip()
    return APIHelper(base_url)


class APIClient:
    """
    Simple API Client for interacting with REST APIs.
    """
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, headers=headers, params=params, method='GET')


@pytest.fixture(scope="session")
def api_client(api_helper):
    """
    Fixture to provide an APIClient instance.
    """
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """
    Fixture to provide a valid API key for authentication.
    """
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    """
    Fixture to provide an invalid API key for testing.
    """
    return "invalid-api-key"


@pytest.fixture(scope="session")
def valid_location():
    """
    Fixture to provide a test location parameter.
    """
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """
    Fixture to provide an OAuth2 token for authentication.
    """
    return config["authentication"]["petstore_auth"]
