import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Precompiled schemas for caching and performance
post_request_schema = {
    "type": "object",
    "properties": {
        "petId": {
            "type": "integer",
            "format": "int64"
        },
        "additionalMetadata": {
            "type": "string"
        }
    },
    "required": ["petId"]
}

post_response_schema = {
    "type": "object",
    "properties": {
        "code": {
            "type": "integer",
            "format": "int32"
        },
        "type": {
            "type": "string"
        },
        "message": {
            "type": "string"
        }
    },
    "required": ["code", "type", "message"]
}

# Compile schemas for Draft7Validator
compiled_post_request_validator = Draft7Validator(post_request_schema)
compiled_post_response_validator = Draft7Validator(post_response_schema)

# Fixtures for test data
@pytest.fixture
def request_payload_correct() -> Dict[str, Any]:
    return {
        "petId": 12345,
        "additionalMetadata": "Sample metadata"
    }

@pytest.fixture
def request_payload_missing_field() -> Dict[str, Any]:
    return {
        "additionalMetadata": "Sample metadata"
    }

@pytest.fixture
def response_payload_correct() -> Dict[str, Any]:
    return {
        "code": 200,
        "type": "success",
        "message": "File uploaded successfully"
    }

@pytest.fixture
def response_payload_invalid_type() -> Dict[str, Any]:
    return {
        "code": "200",  # Incorrect type, should be integer
        "type": "success",
        "message": "File uploaded successfully"
    }

# Test functions
@pytest.mark.parametrize("payload", [
    pytest.lazy_fixture("request_payload_correct"),
    pytest.lazy_fixture("request_payload_missing_field")
])
def test_validate_post_request_schema(payload):
    """Validate POST request payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    """
    try:
        compiled_post_request_validator.validate(payload)
        assert "petId" in payload, "Required field 'petId' is missing"
        logger.info("POST request schema validation passed successfully.")
    except ValidationError as e:
        logger.error(f"Validation failed for POST request schema: {e.message}")
        pytest.fail(f"Schema validation error: {e.message}")

@pytest.mark.parametrize("payload", [
    pytest.lazy_fixture("response_payload_correct"),
    pytest.lazy_fixture("response_payload_invalid_type"),
])
def test_validate_post_response_schema(payload):
    """Validate POST response payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    """
    try:
        compiled_post_response_validator.validate(payload)
        assert {"code", "type", "message"}.issubset(payload.keys()), \
            "Response is missing required fields"
        logger.info("POST response schema validation passed successfully.")
    except ValidationError as e:
        logger.error(f"Validation failed for POST response schema: {e.message}")
        pytest.fail(f"Schema validation error: {e.message}")

@pytest.mark.parametrize("payload, expected_failure", [
    (pytest.lazy_fixture("request_payload_missing_field"), "Required field 'petId' is missing"),
    (pytest.lazy_fixture("response_payload_invalid_type"), "Invalid type for field 'code'")
])
def test_post_schema_edge_cases(payload, expected_failure):
    """Test edge cases for POST request and response schemas."""
    try:
        # Test request schema
        if "petId" not in payload:
            compiled_post_request_validator.validate(payload)
        else:
            compiled_post_response_validator.validate(payload)
        pytest.fail("Validation should fail but passed unexpectedly.")
    except ValidationError as e:
        logger.info(f"Edge case validation failed as expected: {expected_failure}")
        assert expected_failure in str(e.message), f"Unexpected validation error: {e.message}"
