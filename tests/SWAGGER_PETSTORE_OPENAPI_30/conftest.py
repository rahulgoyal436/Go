import pytest
import requests
import yaml
import os
from pathlib import Path
import logging

# Helper function to replace ${var} placeholders with environment variables
def replace_env_variables(config_dict):
    for key, value in config_dict.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            config_dict[key] = os.getenv(env_var, "")
        elif isinstance(value, dict):
            replace_env_variables(value)
    return config_dict


# Fixture to load configuration from config.yml
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / 'config.yml'
    try:
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
            config = replace_env_variables(raw_config)
        if not config:
            raise ValueError("Configuration is empty or invalid.")
        return config
    except FileNotFoundError:
        logging.error(f"config.yml not found at {config_path}")
        pytest.fail("Configuration file config.yml is not found.")
    except yaml.YAMLError as e:
        logging.error("Error parsing YAML configuration.")
        pytest.fail(f"Error parsing YAML configuration: {str(e)}")


# Helper class for making HTTP requests
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
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            return response
        except requests.RequestException as e:
            logging.error(f"HTTP request error: {str(e)}")
            pytest.fail(f"HTTP request error: {str(e)}")


# Fixture to provide API helper object
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config['api']['host']
    return APIHelper(base_url)


# Simple API client with predefined methods
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


# Fixture to provide API client object
@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Fixture for valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config['authentication']['api_key']
    if not api_key:
        pytest.fail("Valid API key is missing in config.")
    return api_key


# Fixture for invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_string_for_testing"


# Fixture for valid location parameter
@pytest.fixture(scope="session")
def valid_location():
    return "New York City"  # Replace with a relevant test location if necessary


# Fixture for OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config['authentication']['petstore_auth']
    if not token:
        pytest.fail("OAuth2 token is missing in config.")
    return token
