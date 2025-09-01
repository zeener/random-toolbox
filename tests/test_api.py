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

    # Hash Generation Tests
    def test_hash_endpoint_default(self):
        """Test hash endpoint with default parameters."""
        response = self.app.get('/api/v1/hash/generate?text=hello%20world')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "hash" in data["data"]
        assert "metadata" in data["data"]

        metadata = data["data"]["metadata"]
        assert metadata["algorithm"] == "sha256"
        assert metadata["input_length"] == 11
        assert metadata["hash_length"] == 64
        assert metadata["encoding"] == "utf-8"

    def test_hash_endpoint_md5(self):
        """Test hash endpoint with MD5 algorithm."""
        response = self.app.get('/api/v1/hash/generate?text=test&algorithm=md5')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["data"]["metadata"]["algorithm"] == "md5"
        assert data["data"]["metadata"]["hash_length"] == 32
        assert data["data"]["hash"] == "098f6bcd4621d373cade4e832627b4f6"

    def test_hash_endpoint_missing_text(self):
        """Test hash endpoint with missing text parameter."""
        response = self.app.get('/api/v1/hash/generate')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "MISSING_TEXT"

    def test_hash_endpoint_invalid_algorithm(self):
        """Test hash endpoint with invalid algorithm."""
        response = self.app.get('/api/v1/hash/generate?text=test&algorithm=invalid')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_PARAMETER"

    # UUID Generation Tests
    def test_uuid_endpoint_default(self):
        """Test UUID endpoint with default parameters."""
        response = self.app.get('/api/v1/uuid/generate')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "uuid" in data["data"]
        assert "metadata" in data["data"]

        metadata = data["data"]["metadata"]
        assert metadata["version"] == "V4"
        assert metadata["type"] == "Random UUID"
        assert metadata["length"] == 36
        assert metadata["format"] == "8-4-4-4-12 hexadecimal digits"

    def test_uuid_endpoint_v1(self):
        """Test UUID endpoint with v1 version."""
        response = self.app.get('/api/v1/uuid/generate?version=v1')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["data"]["metadata"]["version"] == "V1"
        assert data["data"]["metadata"]["type"] == "Time-based UUID"

    def test_uuid_endpoint_invalid_version(self):
        """Test UUID endpoint with invalid version."""
        response = self.app.get('/api/v1/uuid/generate?version=v5')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_PARAMETER"

    # UUID Validation Tests
    def test_uuid_validate_endpoint_valid(self):
        """Test UUID validation endpoint with valid UUID."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        response = self.app.get(f'/api/v1/uuid/validate?uuid={valid_uuid}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["is_valid"] is True
        assert data["data"]["uuid"] == valid_uuid

    def test_uuid_validate_endpoint_invalid(self):
        """Test UUID validation endpoint with invalid UUID."""
        invalid_uuid = "invalid-uuid-format"
        response = self.app.get(f'/api/v1/uuid/validate?uuid={invalid_uuid}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["is_valid"] is False
        assert "error" in data["data"]
        assert "suggestions" in data["data"]

    def test_uuid_validate_endpoint_missing_uuid(self):
        """Test UUID validation endpoint with missing UUID parameter."""
        response = self.app.get('/api/v1/uuid/validate')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "MISSING_UUID"

    # Base64 Encoding Tests
    def test_base64_encode_endpoint(self):
        """Test Base64 encoding endpoint."""
        payload = {"text": "Hello World!"}
        response = self.app.post('/api/v1/base64/encode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "encoded" in data["data"]
        assert "metadata" in data["data"]

        assert data["data"]["encoded"] == "SGVsbG8gV29ybGQh"
        metadata = data["data"]["metadata"]
        assert metadata["original_length"] == 12
        assert metadata["encoded_length"] == 16
        assert metadata["padding_chars"] == 0

    def test_base64_encode_endpoint_missing_text(self):
        """Test Base64 encoding endpoint with missing text."""
        payload = {}
        response = self.app.post('/api/v1/base64/encode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "MISSING_TEXT"

    def test_base64_encode_endpoint_invalid_json(self):
        """Test Base64 encoding endpoint with invalid JSON."""
        response = self.app.post('/api/v1/base64/encode',
                               data="invalid json",
                               content_type='application/json')
        assert response.status_code == 500  # Flask returns 500 for invalid JSON

    # Base64 Decoding Tests
    def test_base64_decode_endpoint(self):
        """Test Base64 decoding endpoint."""
        payload = {"encoded": "SGVsbG8gV29ybGQh"}
        response = self.app.post('/api/v1/base64/decode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "decoded" in data["data"]
        assert "metadata" in data["data"]

        assert data["data"]["decoded"] == "Hello World!"
        metadata = data["data"]["metadata"]
        assert metadata["decoded_length"] == 12
        assert metadata["encoded_length"] == 16

    def test_base64_decode_endpoint_invalid_base64(self):
        """Test Base64 decoding endpoint with invalid Base64."""
        payload = {"encoded": "Invalid!@#$"}
        response = self.app.post('/api/v1/base64/decode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "DECODING_ERROR"

    # URL Encoding Tests
    def test_url_encode_endpoint(self):
        """Test URL encoding endpoint."""
        payload = {"text": "Hello World! @#$%", "type": "standard"}
        response = self.app.post('/api/v1/url/encode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "encoded" in data["data"]
        assert "metadata" in data["data"]

        assert data["data"]["encoded"] == "Hello%20World%21%20%40%23%24%25"
        metadata = data["data"]["metadata"]
        assert metadata["encoding_type"] == "standard"
        assert metadata["original_length"] == 17
        assert metadata["characters_encoded"] == 7

    def test_url_encode_endpoint_plus_type(self):
        """Test URL encoding endpoint with plus type."""
        payload = {"text": "Hello World!", "type": "plus"}
        response = self.app.post('/api/v1/url/encode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["data"]["metadata"]["encoding_type"] == "plus"
        # Plus encoding should have + instead of %20 for spaces
        assert "+" in data["data"]["encoded"]
        assert "%20" not in data["data"]["encoded"]

    def test_url_encode_endpoint_missing_text(self):
        """Test URL encoding endpoint with missing text."""
        payload = {"type": "standard"}
        response = self.app.post('/api/v1/url/encode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["code"] == "MISSING_TEXT"

    # URL Decoding Tests
    def test_url_decode_endpoint(self):
        """Test URL decoding endpoint."""
        payload = {"encoded": "Hello%20World%21%20%40%23%24%25"}
        response = self.app.post('/api/v1/url/decode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "decoded" in data["data"]
        assert "metadata" in data["data"]

        assert data["data"]["decoded"] == "Hello World! @#$%"
        metadata = data["data"]["metadata"]
        assert metadata["decoding_type"] == "standard"
        assert metadata["decoded_length"] == 17
        assert metadata["characters_decoded"] == 7

    def test_url_decode_endpoint_plus_type(self):
        """Test URL decoding endpoint with plus type."""
        payload = {"encoded": "Hello+World%21", "type": "plus"}
        response = self.app.post('/api/v1/url/decode',
                               json=payload,
                               content_type='application/json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["data"]["decoded"] == "Hello World!"
        assert data["data"]["metadata"]["decoding_type"] == "plus"