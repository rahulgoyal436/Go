import pytest
import json
import jsonschema
from jsonschema import Draft7Validator, ValidationError
import logging
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Compiled JSON schemas
GET_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "required": ["name", "photoUrls"],
        "type": "object",
        "properties": {
            "id": {"type": "integer", "format": "int64"},
            "name": {"type": "string"},
            "category": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "name": {"type": "string"},
                },
            },
            "photoUrls": {
                "type": "array",
                "items": {"type": "string"},
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "name": {"type": "string"},
                    },
                },
            },
            "status": {"type": "string"},
        },
    },
}

GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# JSON schema validators (precompiled for performance)
GET_RESPONSE_VALIDATOR = Draft7Validator(GET_RESPONSE_SCHEMA)
GET_REQUEST_VALIDATOR = Draft7Validator(GET_REQUEST_SCHEMA)


@pytest.fixture
def request_payload() -> Dict[str, Any]:
    """Fixture providing a sample request payload."""
    return {"tags": ["tag1", "tag2"]}


@pytest.fixture
def response_payload() -> List[Dict[str, Any]]:
    """Fixture providing a sample response payload."""
    return [
        {
            "id": 10,
            "name": "doggie",
            "category": {"id": 1, "name": "Dogs"},
            "photoUrls": ["https://example.com/photo1.jpg"],
            "tags": [{"id": 1, "name": "tag1"}],
            "status": "available",
        }
    ]


def validate_schema(schema_validator: Draft7Validator, payload: Any):
    """Helper function to validate JSON schema."""
    try:
        schema_validator.validate(payload)
    except ValidationError as e:
        logger.error(f"Validation Error at {list(e.path)}: {e.message}")
        pytest.fail(f"Schema validation failed: {e.message}")


def test_validate_get_request_schema(request_payload):
    """Validate GET request payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    - Nested object structure
    - Array item validation
    """
    validate_schema(GET_REQUEST_VALIDATOR, request_payload)


def test_validate_get_response_schema(response_payload):
    """Validate GET response payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    - Nested object structure
    - Array item validation
    """
    validate_schema(GET_RESPONSE_VALIDATOR, response_payload)


@pytest.mark.parametrize("payload", [
    ({"tags": ["tag1"]}),  # Minimum tags
    ({"tags": ["tag1", "tag2", "tag3"]}),  # Multiple tags
    ({"tags": []}),  # Empty tags array
    ({"tags": [""]}),  # Empty string in tags
])
def test_get_request_schema_edge_cases(payload):
    """Test edge cases for GET request schema."""
    validate_schema(GET_REQUEST_VALIDATOR, payload)


@pytest.mark.parametrize("response", [
    ([{
        "name": "doggie",
        "photoUrls": ["https://example.com/photo1.jpg"]
    }]),  # Minimal valid response
    ([{
        "id": 10,
        "name": "doggie",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["https://example.com/photo1.jpg"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }]),  # Full valid response
    ([{
        "id": 1234567890123456789,  # Test long integer
        "name": "doggie",
        "photoUrls": ["https://example.com/photo.jpg", ""],  # Empty photo URL
        "status": "pending"
    }]),  # Missing optional fields
])
def test_get_response_schema_edge_cases(response):
    """Test edge cases for GET response schema."""
    validate_schema(GET_RESPONSE_VALIDATOR, response)
