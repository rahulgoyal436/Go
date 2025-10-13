import pytest
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Sample JSON schemas (GET, POST, DELETE)
REQUEST_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "get": {
        "type": "object",
        "properties": {
            "parameters": {
                "type": "object",
                "properties": {
                    "petId": {"type": "integer", "format": "int64"}
                },
                "required": ["petId"]
            }
        },
        "required": ["parameters"]
    },
    "post": {
        "type": "object",
        "properties": {
            "parameters": {
                "type": "object",
                "properties": {
                    "petId": {"type": "integer", "format": "int64"},
                    "name": {"type": "string"},
                    "status": {"type": "string"}
                },
                "required": ["petId"]
            }
        },
        "required": ["parameters"]
    },
    "delete": {
        "type": "object",
        "properties": {
            "parameters": {
                "type": "object",
                "properties": {
                    "petId": {"type": "integer", "format": "int64"},
                    "api_key": {"type": "string"}
                },
                "required": ["petId"]
            }
        },
        "required": ["parameters"]
    },
}

RESPONSE_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "get": {
        "type": "object",
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
            "status": {"type": "string"}
        },
        "required": ["name", "photoUrls"]
    },
    "post": {
        "type": "object",
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
            "status": {"type": "string"}
        },
        "required": ["name", "photoUrls"]
    },
    "delete": {
        "type": "object",
        "properties": {
            "message": {"type": "string"}
        }
    },
}

# Helper functions for schema validation
def validate_schema(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        for error in errors:
            message = f"Validation error at {'/'.join(map(str, error.path))}: {error.message}"
            logger.error(message)
        raise ValidationError(f"Payload validation failed: {errors}")

# Test payload fixtures
@pytest.fixture
def request_payload():
    return {
        "parameters": {"petId": 123}
    }

@pytest.fixture
def response_payload():
    return {
        "id": 123,
        "name": "doggie",
        "photoUrls": ["http://example.com/photo.jpg"]
    }

# Parameterized tests
@pytest.mark.parametrize("method", ["get", "post", "delete"])
def test_validate_request_schema(method: str, request_payload) -> None:
    """Validate request payload for each HTTP method."""
    schema = REQUEST_SCHEMAS[method]
    try:
        validate_schema(request_payload, schema)
    except ValidationError as e:
        pytest.fail(str(e))

@pytest.mark.parametrize("method", ["get", "post", "delete"])
def test_validate_response_schema(method: str, response_payload) -> None:
    """Validate response payload for each HTTP method."""
    schema = RESPONSE_SCHEMAS[method]
    try:
        validate_schema(response_payload, schema)
    except ValidationError as e:
        pytest.fail(str(e))

@pytest.mark.parametrize("method", ["get", "post", "delete"])
def test_schema_edge_cases(method: str) -> None:
    """Test edge cases and boundary conditions."""
    schema = REQUEST_SCHEMAS[method]
    edge_case_payload = {
        "parameters": {}
    }  # Missing required fields
    with pytest.raises(ValidationError):
        validate_schema(edge_case_payload, schema)

    # Add more edge cases as required (e.g., invalid types, extra fields, etc.)
