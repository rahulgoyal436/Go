import os
import pytest
import requests
import yaml
from pathlib import Path


@pytest.fixture(scope="session")
def config():
    """
    Load configuration from config.yml file
    """
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, "r") as file:
        try:
            config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse config.yml: {e}")
    
    return config_data


class APIHelper:
    """
    Helper class for making HTTP requests
    """
    def __init__(self, base_url):
        self.base_url = base_url.strip("/")

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


@pytest.fixture(scope="session")
def api_helper(config):
    """
    Provides an instance of APIHelper
    """
    base_url = config["api"]["host"].strip()
    return APIHelper(base_url=base_url)


class APIClient:
    """
    Simple API client class
    """
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    """
    Provides a simple API client
    """
    return APIClient(api_helper=api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """
    Extract valid API key from configuration
    """
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    """
    Provide a dummy invalid API key for testing
    """
    return "invalid-api-key"


@pytest.fixture(scope="session")
def valid_location():
    """
    Provide a test location parameter
    """
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """
    Extract OAuth2 token from configuration
    """
    return config["authentication"]["petstore_auth"]
