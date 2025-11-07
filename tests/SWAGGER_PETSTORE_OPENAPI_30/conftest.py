import pytest
import requests
import os
import yaml
from pathlib import Path
from requests.exceptions import RequestException


@pytest.fixture(scope="session")
def config():
    """Load configuration from config.yml and replace environment variables."""
    try:
        config_path = Path(__file__).parent / "config.yml"
        with config_path.open("r") as file:
            raw_config = yaml.safe_load(file)
        
        def resolve_env_var(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value.strip("${}")
                return os.getenv(env_var, None)
            return value
        
        def replace_values(obj):
            if isinstance(obj, dict):
                return {key: replace_values(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [replace_values(item) for item in obj]
            else:
                return resolve_env_var(obj)
        
        resolved_config = replace_values(raw_config)
        return resolved_config
    except FileNotFoundError:
        pytest.fail("Configuration file 'config.yml' not found.")
    except yaml.YAMLError:
        pytest.fail("Error parsing the 'config.yml' file.")
    except Exception as e:
        pytest.fail(f"Unhandled error loading config: {str(e)}")


class APIHelper:
    """Helper class for making HTTP requests."""
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                pytest.fail(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response
        except RequestException as e:
            pytest.fail(f"HTTP request failed: {str(e)}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture providing APIHelper instance."""
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        pytest.fail("Base URL is not configured in 'config.yml'.")
    return APIHelper(base_url)


@pytest.fixture
def api_client(api_helper):
    """Fixture providing simplified API client functions."""
    class APIClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method="GET")
        
        def post(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method="POST")
        
        def put(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method="PUT")
        
        def delete(self, endpoint, headers=None):
            return api_helper.make_request(endpoint, headers=headers, method="DELETE")
    
    return APIClient()


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture providing a valid API key from config."""
    api_key = config.get("authentication", {}).get("api_key", "").strip()
    if not api_key:
        pytest.fail("Valid API key is not configured.")
    return api_key


@pytest.fixture
def invalid_api_key():
    """Fixture providing an invalid dummy API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location(config):
    """Fixture providing valid location parameter for testing."""
    location = config.get("api", {}).get("default_location", "New York").strip()
    return location


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture providing OAuth2 token from config."""
    token = config.get("authentication", {}).get("petstore_auth", "").strip()
    if not token:
        pytest.fail("OAuth2 token is not configured.")
    return token
