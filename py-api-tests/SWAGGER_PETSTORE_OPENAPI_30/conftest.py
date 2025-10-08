import pytest
import requests
import yaml
from pathlib import Path
import os


# Load configuration fixture
@pytest.fixture(scope="session")
def config():
    config_path = Path(os.path.join(os.path.dirname(__file__), "config.yml"))
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with config_path.open("r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as err:
            raise RuntimeError(f"Error parsing configuration file: {err}")


# API Helper Class
class APIHelper:
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
            return response
        except requests.RequestException as err:
            raise RuntimeError(f"Error during API request: {err}")


# API Helper fixture
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config['api']['host']
    return APIHelper(base_url)


# API Client Class
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


# API Client fixture
@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Valid API Key fixture
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config['authentication']['api_key']


# Invalid API Key fixture
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_123"


# Valid Location fixture
@pytest.fixture(scope="session")
def valid_location():
    # Provide a static location for testing purposes
    return {"latitude": 37.7749, "longitude": -122.4194}


# OAuth2 Token fixture
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config['authentication']['petstore_auth']
