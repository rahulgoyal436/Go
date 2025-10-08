import pytest
import requests
import yaml
from pathlib import Path
import os


class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = self.base_url + endpoint
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


class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope="session")
def config():
    config_file = Path(os.path.join(os.path.dirname(__file__), 'config.yml'))
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at {config_file}")
    try:
        with open(config_file, 'r') as file:
            config_data = yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise ValueError(f"Error loading YAML configuration: {e}")
    return config_data


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config['api']['host'].strip()
    if not base_url.endswith('/'):
        base_url += '/'
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    return config['authentication']['api_key']


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key"


@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 37.7749, "longitude": -122.4194}  # Example: San Francisco


@pytest.fixture(scope="session")
def oauth2_token(config):
    return config['authentication']['petstore_auth']
