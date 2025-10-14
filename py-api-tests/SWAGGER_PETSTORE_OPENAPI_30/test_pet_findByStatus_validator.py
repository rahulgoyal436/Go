import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Compiled JSON schemas for /pet/findByStatus endpoint
GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "default": "available"
        }
    },
    "required": []
}

GET_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["name", "photoUrls"],
        "properties": {
            "id": {"type": "integer", "format": "int64"},
            "name": {"type": "string"},
            "category": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "name": {"type": "string"}
                }
            },
            "photoUrls": {
                "type": "array",
                "items": {"type": "string"}
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "name": {"type": "string"}
                    }
                }
            },
            "status": {"type": "string"}
        }
    }
}

# Helper function to validate payloads
def validate_schema(schema: Dict[str, Any], payload: Dict[str, Any]):
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        for error in errors:
            logger.error(f"Validation Error: {error.message} at path {error.path}")
        raise ValidationError(f"{len(errors)} validation error(s) found.")

@pytest.mark.parametrize("request_payload", [
    {"status": "available"},
    {"status": "sold"},
    {},  # Minimal payload with default values
])
def test_validate_get_request_schema(request_payload: Dict[str, Any]) -> None:
    """Validate GET request payload against schema.

    Tests:
    - Required fields presence.
    - Field type validation.
    - Default field values validity.
    """
    try:
        validate_schema(GET_REQUEST_SCHEMA, request_payload)
    except ValidationError as err:
        pytest.fail(f"Request validation failed: {err}")

@pytest.mark.parametrize("response_payload", [
    [
        {
            "id": 10,
            "name": "doggie",
            "category": {"id": 1, "name": "Dogs"},
            "photoUrls": ["https://example.com/photo.jpg"],
            "tags": [{"id": 2, "name": "puppy"}],
            "status": "available"
        }
    ],
    [
        {
            "id": 20,
            "name": "cat",
            "category": {"id": 2, "name": "Cats"},
            "photoUrls": ["https://example.com/cat.jpg"],
            "tags": [{"id": 3, "name": "kitten"}],
            "status": "sold"
        }
    ],
    []  # Test empty array response
])
def test_validate_get_response_schema(response_payload: List[Dict[str, Any]]) -> None:
    """Validate GET response payload against schema.

    Tests:
    - Required fields presence.
    - Field type validation.
    - Nested object structure.
    - Array item validation.
    """
    try:
        validate_schema(GET_RESPONSE_SCHEMA, response_payload)
    except ValidationError as err:
        pytest.fail(f"Response validation failed: {err}")

@pytest.mark.parametrize("edge_payload", [
    {"status": 123},  # Invalid type for `status`
    {"status": ""},  # Edge case: Empty string
    {"unknown_field": "value"},  # Invalid field
    [{"name": "doggie"}],  # Missing required fields in an object
])
def test_get_schema_edge_cases(edge_payload: Any) -> None:
    """Test edge cases for GET request/response schema.

    Tests:
    - Invalid field types.
    - Missing required fields.
    - Unexpected fields.
    """
    if isinstance(edge_payload, list):  # Assume this tests the response schema
        schema = GET_RESPONSE_SCHEMA
    else:  # Assume this tests the request schema
        schema = GET_REQUEST_SCHEMA

    with pytest.raises(ValidationError):
        validate_schema(schema, edge_payload)
