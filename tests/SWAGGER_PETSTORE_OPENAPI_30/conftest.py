import pytest
import os
import yaml
import requests
from pathlib import Path


class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            pytest.fail(f"HTTP Request failed: {err}")
        except ValueError as err:
            pytest.fail(f"ValueError: {err}")


class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope='session')
def config():
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        pytest.fail("The configuration file 'config.yml' does not exist in the expected location.")
    try:
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        # Replace ${var} placeholders with actual environment variables
        for key, value in config_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str) and sub_value.startswith("${") and sub_value.endswith("}"):
                        env_var = sub_value[2:-1]
                        config_data[key][sub_key] = os.getenv(env_var, '').strip()
        return config_data
    except Exception as err:
        pytest.fail(f"Failed to load configuration: {err}")


@pytest.fixture(scope='session')
def api_helper(config):
    base_url = config.get('api', {}).get('host')
    if not base_url:
        pytest.fail("'host' not defined in the 'api' section of the configuration.")
    return APIHelper(base_url)


@pytest.fixture(scope='session')
def api_client(api_helper):
    return APIClient(api_helper)


@pytest.fixture(scope='session')
def valid_api_key(config):
    api_key = config.get('authentication', {}).get('api_key')
    if not api_key:
        pytest.fail("'api_key' is not defined in the 'authentication' section of the configuration.")
    return api_key


@pytest.fixture(scope='session')
def invalid_api_key():
    return "INVALID_API_KEY_12345"


@pytest.fixture(scope='session')
def valid_location():
    return "test-location-parameter"


@pytest.fixture(scope='session')
def oauth2_token(config):
    token = config.get('authentication', {}).get('petstore_auth')
    if not token:
        pytest.fail("'petstore_auth' is not defined in the 'authentication' section of the configuration.")
    return token
