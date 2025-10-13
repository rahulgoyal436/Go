import pytest
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any
import json
import logging

# Set logging configuration
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Example OpenAPI Schemas for validation
schemas = {
    "put": {
        "request": {
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
        },
        "response": {
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
        "request": {
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
        },
        "response": {
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
    }
}

# Precompiled validators for performance
validators = {
    method: {
        "request": Draft7Validator(schema["request"]),
        "response": Draft7Validator(schema["response"])
    }
    for method, schema in schemas.items()
}

@pytest.fixture
def request_payload():
    return {
        "name": "Sample Name",
        "photoUrls": ["http://example.com/photo1", "http://example.com/photo2"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }

@pytest.fixture
def response_payload():
    return {
        "id": 123,
        "name": "Sample Name",
        "photoUrls": ["http://example.com/photo1", "http://example.com/photo2"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }

@pytest.mark.parametrize("method", ["put", "post"])
def test_validate_request_schema(request_payload: Dict[str, Any], method):
    """Validate request payload against the schema."""
    try:
        validators[method]["request"].validate(request_payload)
    except ValidationError as e:
        logging.error(f'Validation Error: {e.message} at {list(e.path)}')
        assert False, f'Request payload validation failed: {e.message}'

@pytest.mark.parametrize("method", ["put", "post"])
def test_validate_response_schema(response_payload: Dict[str, Any], method):
    """Validate response payload against the schema."""
    try:
        validators[method]["response"].validate(response_payload)
    except ValidationError as e:
        logging.error(f'Validation Error: {e.message} at {list(e.path)}')
        assert False, f'Response payload validation failed: {e.message}'

@pytest.mark.parametrize("method", ["put", "post"])
def test_schema_edge_cases(request_payload: Dict[str, Any], response_payload: Dict[str, Any], method):
    """Test schema edge cases for payloads."""
    # Missing required fields
    invalid_payload = {**request_payload}
    del invalid_payload["name"]
    with pytest.raises(ValidationError):
        validators[method]["request"].validate(invalid_payload)

    # Invalid types
    invalid_payload["photoUrls"] = "invalid_url"
    with pytest.raises(ValidationError):
        validators[method]["request"].validate(invalid_payload)

    # Extra fields
    invalid_payload["extraField"] = "unexpected"
    with pytest.raises(ValidationError):
        validators[method]["request"].validate(invalid_payload)
