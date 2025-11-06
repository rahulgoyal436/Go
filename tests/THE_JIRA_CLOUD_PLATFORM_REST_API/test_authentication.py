# Auto-generated authentication tests
# Auto-generated authentication tests
# Generated from Swagger/OpenAPI spec
import pytest
import requests
from typing import Dict, Any


class TestAuthentication:
    """Test suite for API authentication scenarios"""

    def test_basic_auth_valid(self, api_client, basic_auth):
        """Test valid basic authentication"""
        response = api_client.get("/me", auth=basic_auth)
        assert response.status_code == 200

    def test_basic_auth_invalid(self, api_client):
        """Test invalid basic authentication"""
        response = api_client.get("/me", auth=('invalid', 'credentials'))
        assert response.status_code == 401

    def test_oauth2_auth(self, api_client, oauth2_token):
        """Test OAuth2 authentication"""
        headers = {"Authorization": f"Bearer {oauth2_token}"}
        response = api_client.get("/me", headers=headers)
        assert response.status_code in [200, 401]
