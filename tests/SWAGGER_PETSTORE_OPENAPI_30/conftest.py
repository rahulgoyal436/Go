import pytest
import requests
import yaml
import os
from pathlib import Path


def load_config():
    """Load configuration from config.yml and replace ${var} with environment variable values."""
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as config_file:
        config_data = yaml.safe_load(config_file)

    def replace_env_vars(data):
        if isinstance(data, dict):
            return {k: replace_env_vars(v) for k, v in data.items()}
        if isinstance(data, list):
            return [replace_env_vars(v) for v in data]
        if isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            return os.getenv(env_var, "")
        return data

    return replace_env_vars(config_data)


class APIHelper:
    """
    A helper class to facilitate making HTTP requests.
    """
    def __init__(self, base_url):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request error: {e}")


class APIClient:
    """
    A simplified API client for common operations.
    """
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope="session")
def config():
    """Fixture to load configuration from config.yml."""
    return load_config()


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture for the API helper class."""
    base_url = config['api']['host']
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture for the simple API client."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture to provide a valid API key from configuration."""
    return config['authentication']['api_key']


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture to provide an invalid API key."""
    return "invalid_api_key_for_testing"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture for a valid location parameter."""
    return "test_location_param"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture to provide OAuth2 token from configuration."""
    return config['authentication']['petstore_auth']
