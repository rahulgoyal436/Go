import pytest
import json
import logging
from typing import Any, Dict
from jsonschema import Draft7Validator, ValidationError

# Logging configuration for detailed error reporting
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Mock OpenAPI schemas (replace these with actual schema imports or definitions)
PUT_REQUEST_SCHEMA = {
    "required": ["name", "photoUrls"],
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "name": {"type": "string"},
        "category": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"}
            },
        },
        "photoUrls": {"type": "array", "items": {"type": "string"}},
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

PUT_RESPONSE_SCHEMA = PUT_REQUEST_SCHEMA  # Assume response matches request for simplicity

POST_REQUEST_SCHEMA = PUT_REQUEST_SCHEMA  # Replace this with actual POST schema
POST_RESPONSE_SCHEMA = PUT_REQUEST_SCHEMA  # Assume response matches request for simplicity

# Compile schemas for performance optimization
PUT_REQUEST_VALIDATOR = Draft7Validator(PUT_REQUEST_SCHEMA)
PUT_RESPONSE_VALIDATOR = Draft7Validator(PUT_RESPONSE_SCHEMA)
POST_REQUEST_VALIDATOR = Draft7Validator(POST_REQUEST_SCHEMA)
POST_RESPONSE_VALIDATOR = Draft7Validator(POST_RESPONSE_SCHEMA)


def log_validation_error(error: ValidationError, message_prefix: str = ""):
    """Logs detailed validation errors."""
    for error_detail in error.context:
        logging.error(
            f"{message_prefix}Validation error: Field {error_detail.path} - {error_detail.message}"
        )
    logging.error(f"{message_prefix}Validation failed: {str(error)}")


@pytest.fixture
def put_request_payload() -> Dict[str, Any]:
    """Fixture for PUT request payload."""
    return {
        "id": 10,
        "name": "doggie",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo1.jpg"],
        "tags": [{"id": 1, "name": "friendly"}],
        "status": "available"
    }


@pytest.fixture
def put_response_payload() -> Dict[str, Any]:
    """Fixture for PUT response payload."""
    return {
        "id": 10,
        "name": "doggie",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo1.jpg"],
        "tags": [{"id": 1, "name": "friendly"}],
        "status": "available"
    }


@pytest.fixture
def post_request_payload() -> Dict[str, Any]:
    """Fixture for POST request payload."""
    return {
        "name": "doggie",
        "photoUrls": ["http://example.com/photo1.jpg"],
        "category": {"id": 1, "name": "Dogs"},
        "tags": [{"id": 1, "name": "friendly"}],
        "status": "available"
    }


@pytest.fixture
def post_response_payload() -> Dict[str, Any]:
    """Fixture for POST response payload."""
    return {
        "id": 10,
        "name": "doggie",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo1.jpg"],
        "tags": [{"id": 1, "name": "friendly"}],
        "status": "available"
    }


@pytest.mark.parametrize("validator,payload", [
    (PUT_REQUEST_VALIDATOR, {"id": "String instead of int", "name": None}),
    (PUT_REQUEST_VALIDATOR, {"category": {"id": "wrong-type"}}),
    (PUT_RESPONSE_VALIDATOR, {"photoUrls": [123]}),
    (POST_REQUEST_VALIDATOR, {"tags": "string instead of array"}),
    (POST_RESPONSE_VALIDATOR, {"status": 100.5}),
])
def test_schema_edge_cases(validator: Draft7Validator, payload: Dict[str, Any]):
    """Test edge cases and validation errors with invalid payload data."""
    logging.info(f"Testing edge case with payload: {payload}")
    with pytest.raises(ValidationError) as exception_info:
        validator.validate(payload)
        log_validation_error(exception_info.value, "Edge Case Error: ")


def test_validate_put_request_schema(put_request_payload):
    """Validate PUT request payload against schema."""
    try:
        PUT_REQUEST_VALIDATOR.validate(put_request_payload)
    except ValidationError as error:
        log_validation_error(error, "PUT Request Error: ")
        assert False, f"Schema validation failed for PUT request: {error}"
    assert True, "Schema validation passed for PUT request."


def test_validate_put_response_schema(put_response_payload):
    """Validate PUT response payload against schema."""
    try:
        PUT_RESPONSE_VALIDATOR.validate(put_response_payload)
    except ValidationError as error:
        log_validation_error(error, "PUT Response Error: ")
        assert False, f"Schema validation failed for PUT response: {error}"
    assert True, "Schema validation passed for PUT response."


def test_validate_post_request_schema(post_request_payload):
    """Validate POST request payload against schema."""
    try:
        POST_REQUEST_VALIDATOR.validate(post_request_payload)
    except ValidationError as error:
        log_validation_error(error, "POST Request Error: ")
        assert False, f"Schema validation failed for POST request: {error}"
    assert True, "Schema validation passed for POST request."


def test_validate_post_response_schema(post_response_payload):
    """Validate POST response payload against schema."""
    try:
        POST_RESPONSE_VALIDATOR.validate(post_response_payload)
    except ValidationError as error:
        log_validation_error(error, "POST Response Error: ")
        assert False, f"Schema validation failed for POST response: {error}"
    assert True, "Schema validation passed for POST response."
