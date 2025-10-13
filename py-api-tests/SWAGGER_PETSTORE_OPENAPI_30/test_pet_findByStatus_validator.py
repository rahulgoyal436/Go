import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Example OpenAPI schemas
SCHEMA_DATA = {
    "get": {
        "requestSchema": None,  # No request payload expected for GET
        "responseSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                }
            },
            "required": ["id", "name", "email"],
            "additionalProperties": False
        }
    },
    "post": {
        "requestSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1, "maxLength": 100},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0, "maximum": 120}
            },
            "required": ["name", "email"],
            "additionalProperties": False
        },
        "responseSchema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    },
                    "required": ["id", "name"]
                }
            },
            "required": ["success"],
            "additionalProperties": False
        }
    }
}

# Cache compiled schemas for performance
compiled_schemas = {
    "get_request": Draft7Validator(SCHEMA_DATA["get"]["requestSchema"]) if SCHEMA_DATA["get"]["requestSchema"] else None,
    "get_response": Draft7Validator(SCHEMA_DATA["get"]["responseSchema"]) if SCHEMA_DATA["get"]["responseSchema"] else None,
    "post_request": Draft7Validator(SCHEMA_DATA["post"]["requestSchema"]) if SCHEMA_DATA["post"]["requestSchema"] else None,
    "post_response": Draft7Validator(SCHEMA_DATA["post"]["responseSchema"]) if SCHEMA_DATA["post"]["responseSchema"] else None,
}

@pytest.fixture
def get_response_payload():
    return {
        "id": 1,
        "name": "John Doe",
        "email": "johndoe@example.com",
        "tags": ["developer", "python"]
    }

@pytest.fixture
def post_request_payload():
    return {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "age": 30
    }

@pytest.fixture
def post_response_payload():
    return {
        "success": True,
        "data": {
            "id": 123,
            "name": "John Doe"
        }
    }

def validate_payload(schema: Draft7Validator, payload: Any) -> None:
    """Helper method to validate a payload against a JSON schema."""
    try:
        schema.validate(payload)
    except ValidationError as e:
        logger.error(f"Validation failed: {str(e)}")
        logger.error(f"Failed at: {str(list(e.path))}")
        pytest.fail(f"Validation error in payload: {e.message}", pytrace=False)

# Test GET Response Schema
def test_validate_get_response_schema(get_response_payload):
    """Validate GET response payload against the schema."""
    schema = compiled_schemas["get_response"]
    validate_payload(schema, get_response_payload)

# Test POST Request Schema
def test_validate_post_request_schema(post_request_payload):
    """Validate POST request payload against the schema."""
    schema = compiled_schemas["post_request"]
    validate_payload(schema, post_request_payload)

# Test POST Response Schema
def test_validate_post_response_schema(post_response_payload):
    """Validate POST response payload against the schema."""
    schema = compiled_schemas["post_response"]
    validate_payload(schema, post_response_payload)

@pytest.mark.parametrize("invalid_payload", [
    {},  # Missing required fields
    {"name": "", "email": "invalid-email"},  # Invalid email format, empty name
    {"name": "John Doe", "email": "johndoe@example.com", "age": -1},  # Age below minimum
    {"name": "John Doe", "email": "johndoe@example.com", "extra": "unexpected"}  # Additional property
])
def test_post_schema_edge_cases(invalid_payload):
    """Test edge cases for POST request schema."""
    schema = compiled_schemas["post_request"]
    with pytest.raises(ValidationError):
        validate_payload(schema, invalid_payload)
