import os
import pytest
import requests
import yaml
from pathlib import Path


# Helper function to load YAML config and replace environment variables
def load_config():
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, 'r') as file:
        try:
            raw_config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading YAML config file: {e}")
    
    def replace_env_variables(value):
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, f"<MISSING_ENV:{env_var}>")
        return value
    
    def traverse_and_replace(data):
        if isinstance(data, dict):
            return {key: traverse_and_replace(value) for key, value in data.items()}
        if isinstance(data, list):
            return [traverse_and_replace(item) for item in data]
        return replace_env_variables(data)
    
    return traverse_and_replace(raw_config)


# Pytest fixture: configuration loader
@pytest.fixture(scope='session')
def config():
    return load_config()


# Helper class for making API requests
class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


# Pytest fixture: ApiHelper instance
@pytest.fixture(scope='session')
def api_helper(config):
    base_url = config['api']['host']
    return ApiHelper(base_url)


# Pytest fixture: Simple API client
class ApiClient:
    def __init__(self, helper):
        self.helper = helper

    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope='session')
def api_client(api_helper):
    return ApiClient(api_helper)


# Pytest fixture: Valid API key
@pytest.fixture(scope='session')
def valid_api_key(config):
    return config['authentication']['basicAuth']


# Pytest fixture: Invalid API key
@pytest.fixture(scope='session')
def invalid_api_key():
    return "invalid_api_key_123456"


# Pytest fixture: Valid test location parameter
@pytest.fixture(scope='session')
def valid_location():
    return "TestLocation123"


# Pytest fixture: OAuth2 token
@pytest.fixture(scope='session')
def oauth2_token(config):
    return config['authentication']['OAuth2']
