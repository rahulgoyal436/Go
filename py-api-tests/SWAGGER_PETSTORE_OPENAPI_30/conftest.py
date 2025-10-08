import os
import pytest
import requests
import yaml
from pathlib import Path

# Helper function to load YAML config file
def load_config():
    config_file = Path(__file__).parent / "config.yml"
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    with open(config_file, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading YAML configuration: {e}")

# Helper class for making HTTP requests
class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

# Simple API client built on the helper class
class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

@pytest.fixture(scope="session")
def config():
    """Fixture to load configuration from config.yml"""
    return load_config()

@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture providing an API helper instance."""
    base_url = config['api']['host']
    return ApiHelper(base_url)

@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture providing an API client instance."""
    return ApiClient(api_helper)

@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture providing a valid API key."""
    return config['authentication']['api_key']

@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture providing an invalid API key."""
    return "invalid_api_key"

@pytest.fixture(scope="session")
def valid_location():
    """Fixture providing a valid test location parameter."""
    return {"location": "TestLocation"}

@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture providing an OAuth2 token."""
    return config['authentication']['petstore_auth']
