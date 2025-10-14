import pytest
import jsonschema
import logging
from jsonschema import Draft7Validator
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Precompiled JSON Schemas
GET_REQUEST_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid"
        }
    },
    "additionalProperties": False
}

GET_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["status", "data"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["success", "error"]
        },
        "data": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid"
                },
                "name": {
                    "type": "string"
                }
            },
            "required": ["id", "name"],
            "additionalProperties": False
        }
    },
    "additionalProperties": False
}

# Validator instances
get_request_validator = Draft7Validator(GET_REQUEST_SCHEMA)
get_response_validator = Draft7Validator(GET_RESPONSE_SCHEMA)


def validate_schema(payload: Any, schema_validator: Draft7Validator) -> None:
    """
    Validate the payload against the provided schema validator.
    Logs errors and fails the test gracefully on mismatch.
    """
    if payload is None:
        pytest.fail("Payload is missing.")

    try:
        schema_validator.validate(payload)
        if logger.isEnabledFor(logging.INFO):
            logger.info("Schema validation passed.")
    except jsonschema.ValidationError as e:
        error_path = ".".join(map(str, e.path)) if e.path else "(root)"
        logger.error(f"Validation error at '{error_path}': {e.message}")
        logger.error(f"Validator: {e.validator}, Instance: {e.instance}")
        pytest.fail(f"Schema validation failed: {e.message}")
    except Exception as err:
        logger.error(f"Unexpected error during schema validation: {err}")
        pytest.fail(f"Unexpected failure: {err}")


def test_validate_get_request_schema(request_payload: Any) -> None:
    """
    Validate GET request payload against GET_REQUEST_SCHEMA.
    """
    validate_schema(request_payload, get_request_validator)


def test_validate_get_response_schema(response_payload: Any) -> None:
    """
    Validate GET response payload against GET_RESPONSE_SCHEMA.
    """
    validate_schema(response_payload, get_response_validator)


def test_get_schema_edge_cases(edge_case_payload: Any) -> None:
    """
    Validate edge case payloads against appropriate schemas.
    Edge case payload structure: {"type": "request"|"response", "payload": {...}}
    """
    if edge_case_payload is None or "type" not in edge_case_payload or "payload" not in edge_case_payload:
        pytest.fail("Edge case payload structure is invalid or missing.")

    payload_type = edge_case_payload["type"]
    payload = edge_case_payload["payload"]

    if payload_type == "request":
        validate_schema(payload, get_request_validator)
    elif payload_type == "response":
        validate_schema(payload, get_response_validator)
    else:
        pytest.fail(f"Invalid edge case payload type: {payload_type}")
