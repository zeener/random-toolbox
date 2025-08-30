import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.api.app import app


class TestAPI:
    
    def setup_method(self):
        """Setup for each test method."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.app.get('/api/v1/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == "healthy"
        assert data["data"]["version"] == "1.0.0"
        assert "timestamp" in data
    
    # Text Generation Tests
    def test_text_endpoint_default(self):
        """Test text endpoint with default parameters."""
        response = self.app.get('/api/v1/text/random')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "result" in data["data"]
        assert "metadata" in data["data"]
        assert data["data"]["metadata"]["type"] == "paragraph"
        assert data["data"]["metadata"]["count"] == 1
    
    def test_text_endpoint_words(self):
        """Test text endpoint with word generation."""
        response = self.app.get('/api/v1/text/random?type=word&count=5')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        result = data["data"]["result"]
        assert isinstance(result, list)
        assert len(result) == 5
        assert data["data"]["metadata"]["is_array"] is True
    
    def test_text_endpoint_sentences(self):
        """Test text endpoint with sentence generation."""
        response = self.app.get('/api/v1/text/random?type=sentence&count=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        result = data["data"]["result"]
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(sentence.endswith('.') for sentence in result)
    
    def test_text_endpoint_invalid_type(self):
        """Test text endpoint with invalid type."""
        response = self.app.get('/api/v1/text/random?type=invalid')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_TYPE"
    
    def test_text_endpoint_invalid_count(self):
        """Test text endpoint with invalid count."""
        response = self.app.get('/api/v1/text/random?count=invalid')
        assert response.status_code == 400
    
    # Password Generation Tests
    def test_password_endpoint_default(self):
        """Test password endpoint with default parameters."""
        response = self.app.get('/api/v1/password/generate')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "password" in data["data"]
        assert "metadata" in data["data"]
        
        password = data["data"]["password"]
        metadata = data["data"]["metadata"]
        
        assert len(password) == 16
        assert metadata["length"] == 16
        assert "entropy_bits" in metadata
        assert "strength" in metadata
    
    def test_password_endpoint_custom_params(self):
        """Test password endpoint with custom parameters."""
        response = self.app.get('/api/v1/password/generate?length=20&symbols=true&exclude_ambiguous=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        password = data["data"]["password"]
        metadata = data["data"]["metadata"]
        
        assert len(password) == 20
        assert metadata["length"] == 20
        assert metadata["config"]["symbols"] is True
        assert metadata["config"]["exclude_ambiguous"] is True
        
        # Should contain symbols
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        assert any(c in symbols for c in password)
        
        # Should not contain ambiguous characters
        ambiguous = "0O1lI|`'"
        assert not any(c in ambiguous for c in password)
    
    def test_password_endpoint_boolean_params(self):
        """Test password endpoint boolean parameter handling."""
        # Test with explicit false
        response = self.app.get('/api/v1/password/generate?uppercase=false&numbers=false')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        metadata = data["data"]["metadata"]
        assert metadata["config"]["uppercase"] is False
        assert metadata["config"]["numbers"] is False
    
    def test_password_endpoint_invalid_length(self):
        """Test password endpoint with invalid length."""
        response = self.app.get('/api/v1/password/generate?length=200')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_PARAMETER"
    
    # API Key Generation Tests
    def test_apikey_endpoint_default(self):
        """Test API key endpoint with default parameters."""
        response = self.app.get('/api/v1/apikey/generate')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "api_key" in data["data"]
        assert "metadata" in data["data"]
        
        metadata = data["data"]["metadata"]
        assert metadata["format"] == "hex"
        assert metadata["length"] == 64  # hex output length
        assert "entropy_bits" in metadata
        assert "security_level" in metadata
    
    def test_apikey_endpoint_base64_with_prefix(self):
        """Test API key endpoint with base64 format and prefix."""
        response = self.app.get('/api/v1/apikey/generate?format=base64&prefix=sk_&length=24')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        api_key = data["data"]["api_key"]
        metadata = data["data"]["metadata"]
        
        assert api_key.startswith('sk_')
        assert metadata["format"] == "base64"
        assert metadata["prefix"] == "sk_"
        assert metadata["length"] == 32  # This is the base64 output length
        assert metadata["total_length"] > 24
    
    def test_apikey_endpoint_base58(self):
        """Test API key endpoint with base58 format."""
        response = self.app.get('/api/v1/apikey/generate?format=base58')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        api_key = data["data"]["api_key"]
        metadata = data["data"]["metadata"]
        
        assert metadata["format"] == "base58"
        
        # Should not contain ambiguous characters
        ambiguous = "0OIl"
        assert not any(c in ambiguous for c in api_key)
    
    def test_apikey_endpoint_custom_format(self):
        """Test API key endpoint with custom format."""
        response = self.app.get('/api/v1/apikey/generate?format=custom&charset=ABC123&length=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        api_key = data["data"]["api_key"]
        metadata = data["data"]["metadata"]
        
        assert metadata["format"] == "custom"
        assert len(api_key) == 10
        assert all(c in 'ABC123' for c in api_key)
    
    def test_apikey_endpoint_invalid_format(self):
        """Test API key endpoint with invalid format."""
        response = self.app.get('/api/v1/apikey/generate?format=invalid')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_FORMAT"
    
    def test_apikey_endpoint_invalid_length(self):
        """Test API key endpoint with invalid length."""
        response = self.app.get('/api/v1/apikey/generate?length=200')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_PARAMETER"
    
    # Response Format Tests
    def test_success_response_format(self):
        """Test standardized success response format."""
        response = self.app.get('/api/v1/health')
        data = json.loads(response.data)
        
        # Required fields
        assert "success" in data
        assert "timestamp" in data
        assert data["success"] is True
        assert "data" in data
        
        # Timestamp format (ISO 8601)
        timestamp = data["timestamp"]
        assert timestamp.endswith('Z')
        assert 'T' in timestamp
    
    def test_error_response_format(self):
        """Test standardized error response format."""
        response = self.app.get('/api/v1/text/random?type=invalid')
        data = json.loads(response.data)
        
        # Required fields
        assert "success" in data
        assert "timestamp" in data
        assert "error" in data
        assert data["success"] is False
        
        error = data["error"]
        assert "code" in error
        assert "message" in error
    
    def test_404_handling(self):
        """Test 404 error handling."""
        response = self.app.get('/api/v1/nonexistent')
        assert response.status_code == 404
    
    # Content Type Tests
    def test_json_content_type(self):
        """Test that responses have correct content type."""
        response = self.app.get('/api/v1/health')
        assert response.content_type == 'application/json'
    
    # Randomness Tests
    def test_generation_randomness(self):
        """Test that multiple requests produce different results."""
        passwords = []
        api_keys = []
        
        for _ in range(5):
            # Test password randomness
            response = self.app.get('/api/v1/password/generate')
            data = json.loads(response.data)
            passwords.append(data["data"]["password"])
            
            # Test API key randomness
            response = self.app.get('/api/v1/apikey/generate')
            data = json.loads(response.data)
            api_keys.append(data["data"]["api_key"])
        
        # All should be unique
        assert len(set(passwords)) == 5
        assert len(set(api_keys)) == 5
    
    def test_parameter_validation(self):
        """Test comprehensive parameter validation."""
        # Test text endpoint edge cases
        response = self.app.get('/api/v1/text/random?count=1001')
        assert response.status_code == 400
        
        # Test password endpoint edge cases  
        response = self.app.get('/api/v1/password/generate?length=7')
        assert response.status_code == 400
        
        # Test API key endpoint edge cases
        response = self.app.get('/api/v1/apikey/generate?length=150')
        assert response.status_code == 400