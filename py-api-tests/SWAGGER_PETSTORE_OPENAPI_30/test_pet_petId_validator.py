import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict, Optional

# Set up logger for detailed error reporting
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Schema cache for performance optimization
schema_cache: Dict[str, Any] = {}

# Sample schemas for each HTTP method
schemas = {
    "get": {
        "requestSchema": None,
        "responseSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "category": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
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
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                },
                "status": {"type": "string"}
            },
            "required": ["name", "photoUrls"]
        }
    },
    "post": {
        "requestSchema": None,
        "responseSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "category": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
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
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                },
                "status": {"type": "string"}
            },
            "required": ["name", "photoUrls"]
        }
    },
    "delete": {
        "requestSchema": None,
        "responseSchema": None
    }
}

# Utility function to get cached validator
def get_validator(schema: Dict[str, Any]) -> Draft7Validator:
    schema_str = str(schema)
    if schema_str not in schema_cache:
        schema_cache[schema_str] = Draft7Validator(schema)
    return schema_cache[schema_str]

# Fixtures for test payloads
@pytest.fixture
def request_payload() -> Optional[Dict[str, Any]]:
    return {
        "name": "Test Pet",
        "photoUrls": ["https://example.com/photo1.png"]
    }

@pytest.fixture
def response_payload() -> Optional[Dict[str, Any]]:
    return {
        "id": 1,
        "name": "Test Pet",
        "category": {
            "id": 2,
            "name": "Dogs"
        },
        "photoUrls": ["https://example.com/photo1.png"],
        "tags": [{"id": 10, "name": "Cute"}],
        "status": "available"
    }

# Test validate GET response schema
def test_validate_get_response_schema(response_payload: Dict[str, Any]) -> None:
    """Validate GET response payload against schema."""
    schema = schemas["get"]["responseSchema"]
    validator = get_validator(schema)
    try:
        validator.validate(response_payload)
    except ValidationError as e:
        logger.error(f"GET response schema validation failed at {list(e.path)}: {e.message}")
        pytest.fail(f"Schema validation failed: {e}")

# Test validate POST response schema
def test_validate_post_response_schema(response_payload: Dict[str, Any]) -> None:
    """Validate POST response payload against schema."""
    schema = schemas["post"]["responseSchema"]
    validator = get_validator(schema)
    try:
        validator.validate(response_payload)
    except ValidationError as e:
        logger.error(f"POST response schema validation failed at {list(e.path)}: {e.message}")
        pytest.fail(f"Schema validation failed: {e}")

# Test edge cases for GET response schema
@pytest.mark.parametrize("response_payload", [
    {},  # Empty response
    {"name": 123},  # Invalid type for 'name'
    {"name": "", "photoUrls": []},  # Minimum valid response, empty fields
    {"name": "Test", "photoUrls": ["https://example.com"], "extraField": "value"}  # Extra field present
])
def test_get_schema_edge_cases(response_payload: Dict[str, Any]) -> None:
    """Test edge cases for GET response schema."""
    schema = schemas["get"]["responseSchema"]
    validator = get_validator(schema)
    try:
        validator.validate(response_payload)
    except ValidationError as e:
        logger.error(f"GET edge case schema validation failed at {list(e.path)}: {e.message}")
        pytest.fail(f"Edge case schema validation failed: {e}")

# Test edge cases for POST response schema
@pytest.mark.parametrize("response_payload", [
    {},  # Empty response
    {"name": 123},  # Invalid type for 'name'
    {"name": "", "photoUrls": []},  # Minimum valid response, empty fields
    {"name": "Test", "photoUrls": ["https://example.com"], "extraField": "value"}  # Extra field present
])
def test_post_schema_edge_cases(response_payload: Dict[str, Any]) -> None:
    """Test edge cases for POST response schema."""
    schema = schemas["post"]["responseSchema"]
    validator = get_validator(schema)
    try:
        validator.validate(response_payload)
    except ValidationError as e:
        logger.error(f"POST edge case schema validation failed at {list(e.path)}: {e.message}")
        pytest.fail(f"Edge case schema validation failed: {e}")
