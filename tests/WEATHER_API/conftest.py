import pytest
import requests
import yaml
from pathlib import Path
import os


# Load configuration from config.yml
@pytest.fixture(scope='session')
def config():
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, 'r') as file:
        raw_config = yaml.safe_load(file)

    # Replace ${var} with environment variables
    def replace_env_vars(value):
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value.strip('${}')
            return os.getenv(env_var, None)    
        if isinstance(value, dict):
            return {k: replace_env_vars(v) for k, v in value.items()}
        return value

    resolved_config = replace_env_vars(raw_config)
    return resolved_config


# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope='session')
def api_helper(config):
    base_url = config['api']['host']
    if not base_url:
        raise ValueError("Base URL for API is not defined in configuration.")
    return APIHelper(base_url)


# Simple API client for convenience
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope='session')
def api_client(api_helper):
    return APIClient(api_helper)


# Fixture for valid API key
@pytest.fixture(scope='session')
def valid_api_key(config):
    api_key = config['authentication'].get('ApiKeyAuth')
    if not api_key:
        raise ValueError("Valid API key not found in configuration.")
    return api_key


# Fixture for invalid API key
@pytest.fixture(scope='session')
def invalid_api_key():
    return "INVALID_API_KEY"


# Fixture for a valid location parameter
@pytest.fixture(scope='session')
def valid_location():
    return "London,UK"


# Fixture for OAuth2 token
@pytest.fixture(scope='session')
def oauth2_token(config):
    token = config['authentication'].get('OAuth2Token')
    if not token:
        raise ValueError("OAuth2 token not found in configuration.")
    return token
