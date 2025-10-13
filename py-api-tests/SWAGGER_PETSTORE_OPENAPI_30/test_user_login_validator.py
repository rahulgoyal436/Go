import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any, Optional

# Configure logging for detailed error output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample schema data
SCHEMA_DATA = {
    "get": {
        "requestSchema": None,
        "responseSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {
                    "type": "string",
                    "format": "email"
                },
                "roles": {
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
                "name": {"type": "string", "minLength": 3, "maxLength": 50},
                "email": {
                    "type": "string",
                    "format": "email"
                },
                "age": {"type": "integer", "minimum": 18, "maximum": 99},
                "roles": {
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
                "id": {"type": "integer"},
                "status": {"type": "string", "enum": ["success", "failure"]},
                "message": {"type": "string"}
            },
            "required": ["id", "status"],
            "additionalProperties": False
        }
    }
}

# Cache compiled schemas for performance
VALIDATORS = {
    method: {
        "requestValidator": Draft7Validator(schema["requestSchema"]) if schema["requestSchema"] else None,
        "responseValidator": Draft7Validator(schema["responseSchema"]) if schema["responseSchema"] else None
    }
    for method, schema in SCHEMA_DATA.items()
}

@pytest.fixture
def request_payload() -> Dict[str, Any]:
    """Fixture for providing test request payloads."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25,
        "roles": ["admin", "user"]
    }

@pytest.fixture
def response_payload() -> Dict[str, Any]:
    """Fixture for providing test response payloads."""
    return {
        "id": 123,
        "status": "success",
        "message": "Operation successful"
    }

def validate_schema(payload: Dict[str, Any], validator: Optional[Draft7Validator]) -> None:
    """Shared utility to validate payload against a JSON schema."""
    if not validator:
        pytest.skip("Schema is not defined for this method.")
    try:
        validator.validate(payload)
    except ValidationError as e:
        logger.error("Validation failed: %s", e.message)
        logger.error("Failed path: %s", list(e.path))
        pytest.fail(f"Schema validation error: {e.message}")

@pytest.mark.parametrize("method", ["get", "post"])
def test_validate_request_schema(method: str, request_payload: Dict[str, Any]) -> None:
    """Validate request payload against the schema."""
    schema_validator = VALIDATORS[method]["requestValidator"]
    if method == "get":
        pytest.skip("GET method does not have a request payload schema.")
    validate_schema(request_payload, schema_validator)

@pytest.mark.parametrize("method", ["get", "post"])
def test_validate_response_schema(method: str, response_payload: Dict[str, Any]) -> None:
    """Validate response payload against the schema."""
    schema_validator = VALIDATORS[method]["responseValidator"]
    validate_schema(response_payload, schema_validator)

@pytest.mark.parametrize("method", ["post"])
def test_post_schema_edge_cases(request_payload: Dict[str, Any]) -> None:
    """Test edge cases for POST request payload schema."""
    schema_validator = VALIDATORS["post"]["requestValidator"]

    # Test missing required fields
    invalid_payload = request_payload.copy()
    del invalid_payload["email"]
    with pytest.raises(ValidationError):
        validate_schema(invalid_payload, schema_validator)

    # Test invalid email format
    invalid_payload = request_payload.copy()
    invalid_payload["email"] = "invalid-email"
    with pytest.raises(ValidationError):
        validate_schema(invalid_payload, schema_validator)

    # Test string length validation
    invalid_payload = request_payload.copy()
    invalid_payload["name"] = "A" * 51
    with pytest.raises(ValidationError):
        validate_schema(invalid_payload, schema_validator)

    # Test number out of range
    invalid_payload = request_payload.copy()
    invalid_payload["age"] = 17
    with pytest.raises(ValidationError):
        validate_schema(invalid_payload, schema_validator)
