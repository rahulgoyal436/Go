import os
import pytest
import yaml
import requests
from pathlib import Path
from string import Template


# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        method = method.upper()
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=params, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=params, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            pytest.fail(f"HTTP request failed: {e}")


# Load YAML configuration file and expand environment variables
def load_config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        pytest.fail("Configuration file 'config.yml' not found in the current directory.")
    try:
        with config_path.open('r') as f:
            raw_config = yaml.safe_load(f)
        config_str = yaml.dump(raw_config)
        expanded_str = Template(config_str).substitute(os.environ)
        return yaml.safe_load(expanded_str)
    except yaml.YAMLError as e:
        pytest.fail(f"Failed to parse configuration file: {e}")
    except KeyError as e:
        pytest.fail(f"Environment variable not found for placeholder: {e}")


@pytest.fixture(scope="session")
def config():
    return load_config()


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get('api', {}).get('host', '').strip()
    if not base_url:
        pytest.fail("Base URL not found or empty in configuration.")
    return APIHelper(base_url=base_url)


class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get('authentication', {}).get('api_key', '').strip()
    if not api_key:
        pytest.fail("Valid API key not found in configuration.")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_123456"


@pytest.fixture(scope="session")
def valid_location():
    return "New York City, NY"


@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get('authentication', {}).get('petstore_auth', '').strip()
    if not token:
        pytest.fail("OAuth2 token not found in configuration.")
    return token
