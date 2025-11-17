import os
import pytest
import requests
import yaml
from pathlib import Path


class APIHelper:
    """Helper class for making HTTP requests."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


class APIClient:
    """Simple API Client wrapper."""

    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def config():
    """Load configuration from YAML file."""
    config_file = Path(__file__).parent / "config.yml"
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at: {config_file}")
    
    with config_file.open("r") as file:
        raw_config = yaml.safe_load(file)

    def resolve_env_variables(value):
        """Resolve environment variables in the format ${VAR}."""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            return os.getenv(value[2:-1], "")
        return value

    def replace_dict_values(dictionary):
        """Recursively replace placeholders in dictionary."""
        for key, val in dictionary.items():
            if isinstance(val, dict):
                dictionary[key] = replace_dict_values(val)
            else:
                dictionary[key] = resolve_env_variables(val)
        return dictionary

    resolved_config = replace_dict_values(raw_config)
    return resolved_config


@pytest.fixture(scope="session")
def api_helper(config):
    """Initialize APIHelper with the Base URL from config."""
    base_url = config["api"]["host"]
    if not base_url:
        raise ValueError("Base URL must be specified in the configuration!")
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide an API client instance for easier API interactions."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract a valid API key from the configuration."""
    api_key = config["authentication"]["api_key"]
    if not api_key:
        raise ValueError("Valid API key not found in configuration!")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide a dummy invalid API key."""
    return "invalid_api_key_12345"


@pytest.fixture(scope="session")
def valid_location():
    """Provide a valid test location parameter."""
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from the configuration."""
    token = config["authentication"]["petstore_auth"]
    if not token:
        raise ValueError("OAuth2 token not found in configuration!")
    return token
