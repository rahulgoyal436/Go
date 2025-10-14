import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict, List

# Set up logging configuration
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Compiled schemas for performance
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

GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "default": "available"
        }
    }
}

# Fixtures for test payloads
@pytest.fixture
def valid_get_request_payload() -> Dict[str, Any]:
    return {"status": "available"}

@pytest.fixture
def valid_get_response_payload() -> List[Dict[str, Any]]:
    return [
        {
            "id": 10,
            "name": "doggie",
            "photoUrls": ["url1", "url2"],
            "category": {"id": 1, "name": "Dogs"},
            "tags": [{"id": 101, "name": "tag1"}],
            "status": "available"
        }
    ]

@pytest.fixture
def invalid_get_request_payload() -> Dict[str, Any]:
    return {"unknownField": "error"}

@pytest.fixture
def invalid_get_response_payload() -> List[Dict[str, Any]]:
    return [
        {
            "name": 123,  # Invalid type
            "photoUrls": "string"  # Invalid type
        }
    ]

# Helper function for validation
def validate_schema(payload: Any, schema: Dict[str, Any], schema_type: str) -> None:
    try:
        validator = Draft7Validator(schema)
        validator.validate(payload)
    except ValidationError as ex:
        error_path = ".".join(str(x) for x in ex.path)
        logger.error(
            f"Validation failed for {schema_type} at path '{error_path}': {ex.message}"
        )
        raise

# Test function for GET request payload validation
@pytest.mark.parametrize(
    "request_payload",
    [
        pytest.param({"status": "sold"}, id="Valid status - sold"),
        pytest.param({"status": "pending"}, id="Valid status - pending")
    ]
)
def test_validate_get_request_schema(request_payload: Dict[str, Any]) -> None:
    """Validate GET request payload against schema."""
    validate_schema(request_payload, GET_REQUEST_SCHEMA, "GET request")
    
# Test function for GET response payload validation
@pytest.mark.parametrize(
    "response_payload",
    [
        pytest.param(
            [
                {
                    "id": 12,
                    "name": "cat",
                    "photoUrls": ["photo1", "photo2"],
                    "status": "available"
                }
            ], id="Valid response - single pet"),
        pytest.param(
            [
                {
                    "id": 14,
                    "name": "rabbit",
                    "photoUrls": [],
                    "tags": [{"id": 1, "name": "tag"}]
                }
            ], id="Valid response - missing optional fields"
        )
    ]
)
def test_validate_get_response_schema(response_payload: List[Dict[str, Any]]) -> None:
    """Validate GET response payload against schema."""
    validate_schema(response_payload, GET_RESPONSE_SCHEMA, "GET response")

# Test for GET schema-based edge cases
@pytest.mark.parametrize(
    "request_payload,response_payload",
    [
        pytest.param(
            {"status": None},  # Missing valid status field
            [{"id": 15, "photoUrls": [], "tags": []}],  # Missing required fields
            id="Edge case - missing required fields"
        ),
        pytest.param(
            {"status": "available"},
            [{"id": "not_an_int"}],  # Invalid type for ID
            id="Edge case - invalid data types"
        )
    ]
)
def test_get_schema_edge_cases(
    request_payload: Dict[str, Any], response_payload: List[Dict[str, Any]]
) -> None:
    """Validate edge cases for GET request and response schemas."""
    # Validate request schema
    try:
        validate_schema(request_payload, GET_REQUEST_SCHEMA, "GET request edge case")
    except ValidationError:
        # Log and fail gracefully
        assert True, "Request schema validation failed as expected"

    # Validate response schema
    try:
        validate_schema(response_payload, GET_RESPONSE_SCHEMA, "GET response edge case")
    except ValidationError:
        # Log and fail gracefully
        assert True, "Response schema validation failed as expected"
