import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Sample OpenAPI Schemas
SCHEMAS = {
    "get": {
        "requestSchema": None,
        "responseSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "is_active": {"type": "boolean"},
                "created_at": {"type": "string", "format": "date-time"}
            },
            "required": ["id", "name", "email", "is_active"]
        }
    },
    "post": {
        "requestSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 3, "maxLength": 50},
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "minLength": 8},
                "is_active": {"type": "boolean"}
            },
            "required": ["name", "email", "password"]
        },
        "responseSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "is_active": {"type": "boolean"},
                "created_at": {"type": "string", "format": "date-time"}
            },
            "required": ["id", "name", "email", "is_active"]
        }
    }
}

# Fixtures for test payloads
@pytest.fixture
def request_payload_post() -> Dict[str, Any]:
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "SecurePassword123!",
        "is_active": True
    }

@pytest.fixture
def response_payload_post() -> Dict[str, Any]:
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "is_active": True,
        "created_at": "2023-01-01T12:00:00Z"
    }

@pytest.fixture
def response_payload_get() -> Dict[str, Any]:
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "is_active": True,
        "created_at": "2023-01-01T12:00:00Z"
    }

# Helper function to validate schemas
def validate_schema(instance: Any, schema: Dict[str, Any]) -> None:
    validator = Draft7Validator(schema)
    validator.validate(instance)

# Generic error handling wrapper
def handle_validation_errors(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation failed: {e.message}")
            logger.error(f"Path: {' -> '.join(str(x) for x in e.path)}")
            raise e
    return wrapper

# Test cases for GET method
@handle_validation_errors
@pytest.mark.parametrize("payload", [response_payload_get()])
def test_validate_get_response_schema(payload):
    """Validate GET response against schema."""
    schema = SCHEMAS["get"]["responseSchema"]
    validate_schema(payload, schema)

def test_get_schema_edge_cases():
    """Test edge cases for GET response schema."""
    schema = SCHEMAS["get"]["responseSchema"]
    invalid_payloads = [
        {},  # Missing required fields
        {"id": "string"},  # Incorrect type for id
        {"id": 1, "email": "not-an-email"},  # Invalid email format
    ]
    for invalid_payload in invalid_payloads:
        with pytest.raises(ValidationError):
            validate_schema(invalid_payload, schema)

# Test cases for POST method
@handle_validation_errors
@pytest.mark.parametrize("payload", [request_payload_post()])
def test_validate_post_request_schema(payload):
    """Validate POST request payload against schema."""
    schema = SCHEMAS["post"]["requestSchema"]
    validate_schema(payload, schema)

@handle_validation_errors
@pytest.mark.parametrize("payload", [response_payload_post()])
def test_validate_post_response_schema(payload):
    """Validate POST response payload against schema."""
    schema = SCHEMAS["post"]["responseSchema"]
    validate_schema(payload, schema)

def test_post_schema_edge_cases():
    """Test edge cases for POST request schema."""
    schema = SCHEMAS["post"]["requestSchema"]
    invalid_payloads = [
        {},  # Missing required fields
        {"name": "JD"},  # name too short
        {"email": "not-an-email"},  # Invalid email format
        {"password": "short"},  # Password too short
    ]
    for invalid_payload in invalid_payloads:
        with pytest.raises(ValidationError):
            validate_schema(invalid_payload, schema)
