import pytest
import json
import jsonschema
import logging
from typing import Any, Dict, List
from jsonschema.validators import Draft7Validator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Schema Definitions
GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "default": "available"
        }
    },
    "additionalProperties": False
}

GET_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "name",
            "photoUrls"
        ],
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64"
            },
            "name": {
                "type": "string"
            },
            "category": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64"
                    },
                    "name": {
                        "type": "string"
                    }
                }
            },
            "photoUrls": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "format": "int64"
                        },
                        "name": {
                            "type": "string"
                        }
                    }
                }
            },
            "status": {
                "type": "string",
                "description": "pet status in the store"
            }
        }
    }
}

# Precompile JSON Schemas for performance
GET_REQUEST_VALIDATOR = Draft7Validator(GET_REQUEST_SCHEMA)
GET_RESPONSE_VALIDATOR = Draft7Validator(GET_RESPONSE_SCHEMA)

# Utility function for validation
def validate_payload(payload: Any, validator: Draft7Validator, payload_type: str) -> None:
    try:
        validator.validate(payload)
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Validation failed for {payload_type}. Error: {e.message}, Path: {'/'.join(map(str, e.path))}")
        pytest.fail(f"Validation failed: {e.message} at {'/'.join(map(str, e.path))}")

# Fixtures
@pytest.fixture
def get_request_payload() -> Dict[str, Any]:
    """Fixture for GET request payload."""
    return {"status": "available"}

@pytest.fixture
def get_response_payload() -> List[Dict[str, Any]]:
    """Fixture for GET response payload."""
    return [
        {
            "id": 10,
            "name": "doggie",
            "category": {
                "id": 1,
                "name": "Dogs"
            },
            "photoUrls": ["http://example.com/photo1.jpg"],
            "tags": [{"id": 101, "name": "cute"}],
            "status": "available"
        }
    ]

# Test Cases
@pytest.mark.parametrize("request_payload", [({"status": "available"}), ({"status": "sold"})])
def test_validate_get_request_schema(request_payload: Dict[str, Any]) -> None:
    """Validate GET request payload against the schema.

    Tests:
    - Required fields presence
    - Field type validation
    """
    validate_payload(request_payload, GET_REQUEST_VALIDATOR, "GET request payload")

@pytest.mark.parametrize("response_payload", [
    ([
        {
            "id": 10,
            "name": "doggie",
            "category": {
                "id": 1,
                "name": "Dogs"
            },
            "photoUrls": ["http://example.com/photo1.jpg"],
            "tags": [{"id": 101, "name": "cute"}],
            "status": "available"
        }
    ]),
    ([
        {
            "id": 20,
            "name": "cat",
            "category": {
                "id": 2,
                "name": "Cats"
            },
            "photoUrls": ["http://example.com/photo2.jpg"],
            "tags": [{"id": 102, "name": "playful"}],
            "status": "sold"
        }
    ])
])
def test_validate_get_response_schema(response_payload: List[Dict[str, Any]]) -> None:
    """Validate GET response payload against the schema.

    Tests:
    - Required fields presence
    - Field type validation
    - Array items validation
    """
    validate_payload(response_payload, GET_RESPONSE_VALIDATOR, "GET response payload")

@pytest.mark.parametrize(
    "request_payload, response_payload",
    [
        ({"status": "pending"}, [
            {
                "id": 10,
                "name": "doggie",
                "category": {
                    "id": 1,
                    "name": "Dogs"
                },
                "photoUrls": ["http://example.com/photo2.jpg"],
                "tags": [],
                "status": "pending"
            }
        ]),
        ({"status": ""}, [
            {
                "id": 0,
                "name": "unknown",
                "category": {},
                "photoUrls": [],
                "tags": [],
                "status": ""
            }
        ])
    ]
)
def test_get_schema_edge_cases(request_payload: Dict[str, Any], response_payload: List[Dict[str, Any]]) -> None:
    """Test edge cases for GET request and response schemas.

    Tests:
    - Empty or missing optional fields
    - Boundary values for required fields
    - Array edge cases (empty arrays, single element arrays)
    - Nested objects edge cases
    """
    logger.info("Validating edge case for GET request payload.")
    validate_payload(request_payload, GET_REQUEST_VALIDATOR, "GET request payload (edge case)")

    logger.info("Validating edge case for GET response payload.")
    validate_payload(response_payload, GET_RESPONSE_VALIDATOR, "GET response payload (edge case)")
