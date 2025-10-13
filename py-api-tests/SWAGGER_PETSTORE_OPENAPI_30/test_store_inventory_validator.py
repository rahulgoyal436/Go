import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example schema structure (replace with actual OpenAPI schema data)
SCHEMAS = {
    "post": {
        "requestSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                }
            },
            "required": ["name", "email"],
            "additionalProperties": False
        },
        "responseSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "failure"]},
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "createdAt": {"type": "string", "format": "date-time"}
                    },
                    "required": ["id", "createdAt"]
                },
                "error": {"type": "string"}
            },
            "required": ["status"],
            "additionalProperties": False
        }
    }
}

# Utility function to validate payloads
def validate_schema(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    try:
        validator = Draft7Validator(schema)
        validator.validate(payload)
    except ValidationError as e:
        error_path = " -> ".join(map(str, list(e.path)))
        logger.error(f"ValidationError at {error_path}: {e.message}")
        raise

# Fixtures for test payloads
@pytest.fixture
def valid_post_request_payload() -> Dict[str, Any]:
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "tags": ["test"]
    }

@pytest.fixture
def valid_post_response_payload() -> Dict[str, Any]:
    return {
        "status": "success",
        "data": {
            "id": 123,
            "createdAt": "2023-01-01T00:00:00Z"
        }
    }

@pytest.fixture
def invalid_post_request_payload() -> Dict[str, Any]:
    return {
        "name": "",
        "email": "not-an-email",
        "age": -1,
        "tags": []
    }

@pytest.fixture
def invalid_post_response_payload() -> Dict[str, Any]:
    return {
        "status": "invalid_status",
        "data": {
            "id": "not-an-integer",
            "createdAt": "invalid-date"
        }
    }

# Test functions
def test_validate_post_request_schema(valid_post_request_payload: Dict[str, Any]) -> None:
    """Validate POST request payload against schema."""
    schema = SCHEMAS["post"]["requestSchema"]
    assert schema is not None, "Request schema is missing."
    validate_schema(valid_post_request_payload, schema)

def test_validate_post_response_schema(valid_post_response_payload: Dict[str, Any]) -> None:
    """Validate POST response payload against schema."""
    schema = SCHEMAS["post"]["responseSchema"]
    assert schema is not None, "Response schema is missing."
    validate_schema(valid_post_response_payload, schema)

@pytest.mark.parametrize(
    "payload, schema",
    [
        ({"name": ""}, SCHEMAS["post"]["requestSchema"]),  # Missing required fields
        ({"email": "not-an-email"}, SCHEMAS["post"]["requestSchema"]),  # Invalid format
        ({"tags": ["item"]}, SCHEMAS["post"]["requestSchema"]),  # Missing required fields
        ({"status": "unexpected"}, SCHEMAS["post"]["responseSchema"]),  # Invalid enum
    ]
)
def test_post_schema_edge_cases(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Test edge cases for POST schema validation."""
    with pytest.raises(ValidationError):
        validate_schema(payload, schema)
