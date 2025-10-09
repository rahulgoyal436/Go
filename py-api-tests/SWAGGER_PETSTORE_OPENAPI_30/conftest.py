import os
import yaml
import pytest
import requests
from pathlib import Path

# Load configuration file
@pytest.fixture(scope="session")
def config():
    """Load the YAML configuration file."""
    base_dir = Path(__file__).resolve().parent
    config_path = os.path.join(base_dir, "config.yml")
    
    try:
        with open(config_path, "r") as file:
            yaml_config = yaml.safe_load(file)
            return yaml_config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {str(e)}")

# API Helper class
class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip()

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
                response = requests.delete(url, json=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")

# API Helper fixture
@pytest.fixture(scope="session")
def api_helper(config):
    """Provide an ApiHelper instance."""
    base_url = config["api"]["host"]
    return ApiHelper(base_url)

# API Client with specific methods
class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")

# API Client fixture
@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide an ApiClient instance."""
    return ApiClient(api_helper)

# Valid API Key fixture
@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract valid API key from the configuration."""
    return config["authentication"]["api_key"]

# Invalid API Key fixture
@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide a dummy invalid API key."""
    return "invalid_api_key"

# Valid Location fixture
@pytest.fixture(scope="session")
def valid_location():
    """Provide a valid test location parameter."""
    return "Los Angeles, CA"

# OAuth2 Token fixture
@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from the configuration."""
    return config["authentication"]["petstore_auth"]
