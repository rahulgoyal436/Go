import pytest
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Example schemas (replace these with actual schemas from OpenAPI spec)
SCHEMAS = {
    "post_request_schema": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["id", "name", "email"]
    },
    "post_response_schema": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["success", "failure"]},
            "message": {"type": "string"},
            "data": {"type": "object"}
        },
        "required": ["status", "message"]
    }
}

# Helper function to validate JSON payload against schema
def validate_json_schema(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft7Validator(schema)
    try:
        validator.validate(payload)
    except ValidationError as e:
        logger.error(f"Validation failed: {e.message}")
        logger.error(f"Field path: {' -> '.join(str(x) for x in e.path)}")
        raise e

@pytest.fixture
def post_request_payload() -> Dict[str, Any]:
    """Fixture for valid POST request payload."""
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "tags": ["python", "api"]
    }

@pytest.fixture
def post_response_payload() -> Dict[str, Any]:
    """Fixture for valid POST response payload."""
    return {
        "status": "success",
        "message": "Operation completed successfully",
        "data": {"key": "value"}
    }

@pytest.mark.parametrize("missing_field", ["id", "name", "email"])
def test_validate_post_request_schema_missing_fields(post_request_payload, missing_field):
    """Test POST request schema - missing required fields."""
    payload = post_request_payload.copy()
    payload.pop(missing_field)
    with pytest.raises(ValidationError):
        validate_json_schema(payload, SCHEMAS["post_request_schema"])

def test_validate_post_request_schema_invalid_type(post_request_payload):
    """Test POST request schema - invalid field types."""
    payload = post_request_payload.copy()
    payload['id'] = "invalid_integer"
    with pytest.raises(ValidationError):
        validate_json_schema(payload, SCHEMAS["post_request_schema"])

def test_validate_post_request_schema_valid(post_request_payload):
    """Test POST request schema - valid payload."""
    validate_json_schema(post_request_payload, SCHEMAS["post_request_schema"])

@pytest.mark.parametrize("invalid_field_value", [
    {"status": "invalid_enum"},
    {"message": 123},
    {"data": "not_an_object"}
])
def test_validate_post_response_schema_invalid_fields(post_response_payload, invalid_field_value):
    """Test POST response schema - invalid field values."""
    payload = post_response_payload.copy()
    for key, value in invalid_field_value.items():
        payload[key] = value
    with pytest.raises(ValidationError):
        validate_json_schema(payload, SCHEMAS["post_response_schema"])

def test_validate_post_response_schema_valid(post_response_payload):
    """Test POST response schema - valid payload."""
    validate_json_schema(post_response_payload, SCHEMAS["post_response_schema"])

@pytest.mark.parametrize("edge_case_payload", [
    {},  # Completely empty payload
    {"status": "failure", "message": ""},  # Minimal payload with edge values
    {"status": "success", "message": "A" * 1000, "data": {}},  # Large string payload
])
def test_post_schema_edge_cases(edge_case_payload):
    """Test POST schemas - edge cases."""
    schema = SCHEMAS["post_response_schema"]
    if "status" not in edge_case_payload or "message" not in edge_case_payload:
        with pytest.raises(ValidationError):
            validate_json_schema(edge_case_payload, schema)
    else:
        validate_json_schema(edge_case_payload, schema)

