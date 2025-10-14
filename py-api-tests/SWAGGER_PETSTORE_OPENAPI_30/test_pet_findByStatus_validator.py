import pytest
import logging
from typing import Any
from jsonschema import Draft7Validator, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Precompiled schema
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

# Validator Instances
get_request_validator = Draft7Validator(GET_REQUEST_SCHEMA)
get_response_validator = Draft7Validator(GET_RESPONSE_SCHEMA)


# Utility for validation
def validate_schema(payload: Any, schema_validator: Draft7Validator) -> None:
    """
    Validate the payload against the schema.
    
    Args:
        payload (Any): The payload to validate.
        schema_validator (Draft7Validator): Precompiled JSON schema validator.
    
    Raises:
        ValidationError: If the payload does not conform to the schema.
    """
    try:
        schema_validator.validate(payload)
    except ValidationError as e:
        message = (
            f"Schema validation failed:\n"
            f"Path: {'.'.join([str(p) for p in e.path])}\n"
            f"Schema Error: {e.message}\n"
            f"Validator: {e.validator}\n"
            f"Schema: {e.schema}\n"
            f"Instance: {e.instance}"
        )
        logger.error(message)
        raise AssertionError(message) from e


# Test functions
@pytest.mark.parametrize("request_payload", indirect=True)
def test_validate_get_request_schema(request_payload: Any) -> None:
    """
    Test to validate the GET request payload schema for /pet/findByStatus.
    
    Args:
        request_payload (Any): The GET request payload.
    """
    validate_schema(request_payload, get_request_validator)
    logger.info("GET Request Payload schema validation passed.")


@pytest.mark.parametrize("response_payload", indirect=True)
def test_validate_get_response_schema(response_payload: Any) -> None:
    """
    Test to validate the GET response payload schema for /pet/findByStatus.
    
    Args:
        response_payload (Any): The GET response payload.
    """
    validate_schema(response_payload, get_response_validator)
    logger.info("GET Response Payload schema validation passed.")


@pytest.mark.parametrize("edge_case_payload", indirect=True)
def test_get_schema_edge_cases(edge_case_payload: Any) -> None:
    """
    Test to validate schema edge cases for /pet/findByStatus.

    Args:
        edge_case_payload (Any): The edge case payload.
    """
    # Validate edge cases for request vs. response
    if edge_case_payload.get("type", "").lower() == "request":
        payload = edge_case_payload.get("payload", {})
        schema_validator = get_request_validator
        label = "GET Request"
    else:
        payload = edge_case_payload.get("payload", {})
        schema_validator = get_response_validator
        label = "GET Response"

    try:
        validate_schema(payload, schema_validator)
        logger.info(f"{label} Edge Case schema validation passed.")
    except AssertionError:
        logger.error(f"{label} Edge Case schema validation failed.")
        raise
