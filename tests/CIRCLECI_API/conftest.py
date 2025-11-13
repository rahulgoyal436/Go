import pytest
import requests
import yaml
import os
from pathlib import Path


class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = os.path.join(self.base_url, endpoint.lstrip('/'))
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
        except requests.RequestException as e:
            pytest.fail(f"HTTP request failed with error: {e}")


class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope='session')
def config():
    """Load configuration from a YAML file and resolve environment variables."""
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.is_file():
        pytest.fail(f"Config file not found at path: {config_path}")
    try:
        with open(config_path, 'r') as file:
            raw_config = yaml.safe_load(file)

        def resolve_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                return os.getenv(env_var, None) or pytest.fail(f"Environment variable {env_var} not found")
            return value

        def resolve_config(data):
            if isinstance(data, dict):
                return {k: resolve_config(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [resolve_config(v) for v in data]
            else:
                return resolve_value(data)

        return resolve_config(raw_config)
    except Exception as e:
        pytest.fail(f"Failed to load or parse config file: {e}")


@pytest.fixture(scope='session')
def api_helper(config):
    """Fixture that provides a helper class for making HTTP requests."""
    try:
        base_url = config['api']['host'].strip()
        return APIHelper(base_url)
    except KeyError:
        pytest.fail("Missing 'api.host' configuration in config.yml")


@pytest.fixture(scope='session')
def api_client(api_helper):
    """Fixture that provides a simple API client."""
    return APIClient(api_helper=api_helper)


@pytest.fixture(scope='session')
def valid_api_key(config):
    """Fixture to retrieve a valid API key from configuration."""
    try:
        return config['authentication']['api_key_header']
    except KeyError:
        pytest.fail("Missing 'authentication.api_key_header' configuration in config.yml")


@pytest.fixture(scope='session')
def invalid_api_key():
    """Fixture to provide an invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope='session')
def valid_location():
    """Fixture to provide a test location parameter for requests."""
    # Hardcoded or derived from configuration if appropriate
    return "test-location"


@pytest.fixture(scope='session')
def oauth2_token(config):
    """Fixture to extract OAuth2 token from configuration."""
    try:
        return config['authentication']['basic_auth']
    except KeyError:
        pytest.fail("Missing 'authentication.basic_auth' configuration in config.yml")
