import pytest
import os
import yaml
import requests
from pathlib import Path
import re


def load_config():
    """Load configuration from config.yml and replace environment variables."""
    try:
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)
        
        def replace_env_vars(value):
            """Replace ${VAR} in strings with environment variables."""
            env_var_match = re.compile(r'\${(\w+)}')
            if isinstance(value, str):
                match = env_var_match.findall(value)
                if match:
                    for var in match:
                        env_value = os.getenv(var)
                        if env_value is not None:
                            value = value.replace(f"${{{var}}}", env_value)
                        else:
                            raise ValueError(f"Environment variable '{var}' not set.")
            return value

        def recursive_replace(obj):
            """Recursively replace environment variables in config."""
            if isinstance(obj, dict):
                return {key: recursive_replace(val) for key, val in obj.items()}
            elif isinstance(obj, list):
                return [recursive_replace(item) for item in obj]
            else:
                return replace_env_vars(obj)

        return recursive_replace(raw_config)
    except Exception as e:
        raise RuntimeError(f"Failed to load config: {e}")


class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
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
        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")


class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def config():
    """Fixture to load configuration."""
    return load_config()


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture to provide an APIHelper instance."""
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("Base URL not found in config or environment variables.")
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture to provide an APIClient instance."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture to provide a valid API key."""
    api_key = config.get("authentication", {}).get("ApiKeyAuth", "").strip()
    if not api_key:
        raise ValueError("API key not found in config or environment variables.")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture to provide an invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture to provide a valid location parameter."""
    return "London, UK"  # Replace this with actual dynamic test data if required.


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture to provide OAuth2 token."""
    token = config.get("authentication", {}).get("OAuthToken", "").strip()
    if not token:
        raise ValueError("OAuth2 token not found in config or environment variables.")
    return token
