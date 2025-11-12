import os
import pytest
import requests
import yaml
from pathlib import Path
from string import Template


class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = self.base_url.rstrip('/') + '/' + endpoint.lstrip('/')
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
                raise ValueError(f"Invalid HTTP method: {method}")
            response.raise_for_status()
        except requests.RequestException as e:
            pytest.fail(f"HTTP Request failed: {e}")
        return response


@pytest.fixture(scope='session')
def config():
    config_file_path = Path(__file__).parent / "config.yml"
    if not config_file_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_file_path}")

    with open(config_file_path, 'r') as config_file:
        raw_config = yaml.safe_load(config_file)

    # Replace ${var} with environment variables from the system
    def replace_env_vars(raw):
        if isinstance(raw, str):
            template = Template(raw)
            return template.safe_substitute(os.environ)
        elif isinstance(raw, dict):
            return {key: replace_env_vars(value) for key, value in raw.items()}
        elif isinstance(raw, list):
            return [replace_env_vars(item) for item in raw]
        return raw

    return replace_env_vars(raw_config)


@pytest.fixture(scope='session')
def api_helper(config):
    api_host = config.get('api', {}).get('host', '')
    if not api_host:
        raise ValueError("API host is not configured in the config file.")
    return APIHelper(api_host.strip())


@pytest.fixture(scope='session')
def api_client(api_helper):
    class APIClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return APIClient()


@pytest.fixture(scope='session')
def valid_api_key(config):
    api_key = config.get('authentication', {}).get('api_key', '')
    if not api_key:
        raise ValueError("Valid API key is missing in the authentication section of the config file.")
    return api_key


@pytest.fixture(scope='session')
def invalid_api_key():
    return "invalid_api_key_12345"


@pytest.fixture(scope='session')
def valid_location():
    return "San Francisco, CA"


@pytest.fixture(scope='session')
def oauth2_token(config):
    token = config.get('authentication', {}).get('petstore_auth', '')
    if not token:
        raise ValueError("OAuth2 token is missing in the authentication section of the config file.")
    return token
