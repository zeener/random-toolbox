"""Tests for Base64Utility class.

This module contains comprehensive tests for the Base64Utility class,
testing encoding, decoding, validation, and various edge cases.
"""

import pytest
import base64
from src.core.utilities.base64_utility import Base64Utility


class TestBase64Utility:
    
    def setup_method(self):
        """Setup for each test method."""
        self.utility = Base64Utility()
    
    def test_encode_simple_text(self):
        """Test encoding simple text."""
        result = self.utility.encode("Hello World!")
        
        assert "encoded" in result
        assert "original_text" in result
        assert "original_length" in result
        assert "encoded_length" in result
        assert "size_increase_percent" in result
        assert "encoding" in result
        assert "padding_chars" in result
        assert "is_valid_base64" in result
        
        assert result["original_text"] == "Hello World!"
        assert result["original_length"] == 12
        assert result["encoding"] == "utf-8"
        assert result["is_valid_base64"] is True
        
        # Verify actual encoding
        expected = base64.b64encode("Hello World!".encode('utf-8')).decode('ascii')
        assert result["encoded"] == expected
        assert result["encoded"] == "SGVsbG8gV29ybGQh"
    
    def test_encode_empty_string_error(self):
        """Test encoding empty string raises error."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            self.utility.encode("")
    
    def test_encode_non_string_input(self):
        """Test encoding non-string input raises error."""
        with pytest.raises(ValueError, match="Input must be a string"):
            self.utility.encode(123)
        
        with pytest.raises(ValueError, match="Input must be a string"):
            self.utility.encode(None)
        
        with pytest.raises(ValueError, match="Input must be a string"):
            self.utility.encode([])
    
    def test_encode_unicode_text(self):
        """Test encoding Unicode text."""
        unicode_text = "Hello 世界! 🌍"
        result = self.utility.encode(unicode_text)
        
        assert result["original_text"] == unicode_text
        assert result["original_length"] == len(unicode_text)
        assert result["encoding"] == "utf-8"
        
        # Verify actual encoding
        expected = base64.b64encode(unicode_text.encode('utf-8')).decode('ascii')
        assert result["encoded"] == expected
    
    def test_encode_size_calculation(self):
        """Test size increase calculation."""
        # Base64 encoding increases size by ~33%
        result = self.utility.encode("test")
        
        original_size = result["original_length"]
        encoded_size = result["encoded_length"]
        size_increase = result["size_increase_percent"]
        
        expected_increase = ((encoded_size - original_size) / original_size) * 100
        assert abs(size_increase - expected_increase) < 0.01  # Allow small floating point differences
        assert size_increase > 0  # Should always increase
    
    def test_encode_padding_detection(self):
        """Test padding character detection."""
        # Different lengths to test padding
        test_cases = [
            ("a", 2),      # 1 byte -> 2 padding chars
            ("ab", 1),     # 2 bytes -> 1 padding char
            ("abc", 0),    # 3 bytes -> 0 padding chars
            ("abcd", 2),   # 4 bytes -> 2 padding chars
        ]
        
        for text, expected_padding in test_cases:
            result = self.utility.encode(text)
            assert result["padding_chars"] == expected_padding
            assert result["encoded"].count('=') == expected_padding
    
    def test_decode_simple_text(self):
        """Test decoding simple Base64 text."""
        encoded_text = "SGVsbG8gV29ybGQh"  # "Hello World!" in Base64
        result = self.utility.decode(encoded_text)

        assert "decoded" in result
        assert "original_encoded" in result
        assert "encoded_length" in result
        assert "decoded_length" in result
        assert "size_decrease_percent" in result
        assert "encoding" in result
        assert "padding_chars" in result
        assert "bytes_decoded" in result

        assert result["decoded"] == "Hello World!"
        assert result["original_encoded"] == encoded_text
        assert result["encoded_length"] == len(encoded_text)
        assert result["decoded_length"] == 12
        assert result["encoding"] == "utf-8"
        assert result["bytes_decoded"] == 12
    
    def test_decode_with_padding(self):
        """Test decoding Base64 text with padding."""
        encoded_text = "dGVzdA=="  # "test" in Base64 with padding
        result = self.utility.decode(encoded_text)
        
        assert result["decoded"] == "test"
        assert result["padding_chars"] == 2
    
    def test_decode_empty_string_error(self):
        """Test decoding empty string raises error."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            self.utility.decode("")
    
    def test_decode_non_string_input(self):
        """Test decoding non-string input raises error."""
        with pytest.raises(ValueError, match="Input must be a string"):
            self.utility.decode(123)
        
        with pytest.raises(ValueError, match="Input must be a string"):
            self.utility.decode(None)
    
    def test_decode_invalid_base64(self):
        """Test decoding invalid Base64 raises error."""
        invalid_base64_strings = [
            "Invalid!@#$",  # Invalid characters
            "SGVsbG8gV29ybGQ",  # Missing padding
            "SGVsbG8gV29ybGQ===",  # Too much padding
            "SGVsbG8gV29ybGQ!",  # Invalid character at end
        ]
        
        for invalid_string in invalid_base64_strings:
            with pytest.raises(ValueError, match="Invalid Base64"):
                self.utility.decode(invalid_string)
    
    def test_decode_whitespace_handling(self):
        """Test decoding handles whitespace."""
        encoded_text = "SGVsbG8gV29ybGQh"
        encoded_with_whitespace = f"  {encoded_text}  "

        result = self.utility.decode(encoded_with_whitespace)
        assert result["decoded"] == "Hello World!"
        assert result["original_encoded"] == encoded_text  # Should be trimmed
    
    def test_decode_unicode_text(self):
        """Test decoding Unicode text."""
        unicode_text = "Hello 世界! 🌍"
        # First encode it
        encoded = base64.b64encode(unicode_text.encode('utf-8')).decode('ascii')
        
        # Then decode it
        result = self.utility.decode(encoded)
        assert result["decoded"] == unicode_text
        assert result["encoding"] == "utf-8"
    
    def test_decode_size_calculation(self):
        """Test size decrease calculation."""
        encoded_text = "SGVsbG8gV29ybGQh"
        result = self.utility.decode(encoded_text)
        
        encoded_size = result["encoded_length"]
        decoded_size = result["decoded_length"]
        size_decrease = result["size_decrease_percent"]
        
        expected_decrease = ((encoded_size - decoded_size) / encoded_size) * 100
        assert abs(size_decrease - expected_decrease) < 0.01
        assert size_decrease > 0  # Should always decrease
    
    def test_validate_valid_base64(self):
        """Test validation of valid Base64 strings."""
        valid_base64_strings = [
            "SGVsbG8gV29ybGQh",  # No padding
            "dGVzdA==",          # With padding
            "YQ==",              # Single character
            "YWI=",              # Two characters
            "YWJj",              # Three characters
        ]
        
        for valid_string in valid_base64_strings:
            result = self.utility.validate(valid_string)
            assert result["is_valid"] is True
            assert "error" not in result or result["error"] is None
    
    def test_validate_invalid_base64(self):
        """Test validation of invalid Base64 strings."""
        invalid_base64_strings = [
            "Invalid!@#$",       # Invalid characters
            "SGVsbG8gV29ybGQ",   # Incorrect length
            "SGVsbG8gV29ybGQ===", # Too much padding
            "",                  # Empty string
            "A",                 # Too short
        ]
        
        for invalid_string in invalid_base64_strings:
            result = self.utility.validate(invalid_string)
            assert result["is_valid"] is False
            assert "error" in result
            assert "suggestions" in result
    
    def test_validate_non_string_input(self):
        """Test validation of non-string input."""
        result = self.utility.validate(123)
        assert result["is_valid"] is False
        assert result["error"] == "Input must be a string"
        assert "suggestions" in result
    
    def test_encode_decode_roundtrip(self):
        """Test that encoding then decoding returns original text."""
        test_strings = [
            "Hello World!",
            "test",
            "a",
            "Hello 世界! 🌍",
            "The quick brown fox jumps over the lazy dog",
            "1234567890",
            "!@#$%^&*()_+-=[]{}|;:,.<>?",
        ]
        
        for original_text in test_strings:
            # Encode
            encode_result = self.utility.encode(original_text)
            encoded_text = encode_result["encoded"]
            
            # Decode
            decode_result = self.utility.decode(encoded_text)
            decoded_text = decode_result["decoded"]
            
            # Should match original
            assert decoded_text == original_text
    
    def test_is_valid_base64_method(self):
        """Test _is_valid_base64 method indirectly through encode/decode."""
        # Valid Base64 should be detected as valid
        encode_result = self.utility.encode("test")
        assert encode_result["is_valid_base64"] is True

        # Test validation method directly
        validate_result = self.utility.validate(encode_result["encoded"])
        assert validate_result["is_valid"] is True
    
    def test_multiple_operations_consistency(self):
        """Test that multiple operations on same input are consistent."""
        text = "consistency test"
        
        # Encode multiple times
        results = []
        for _ in range(5):
            result = self.utility.encode(text)
            results.append(result["encoded"])
        
        # All results should be identical
        assert len(set(results)) == 1
        
        # Decode multiple times
        encoded = results[0]
        decode_results = []
        for _ in range(5):
            result = self.utility.decode(encoded)
            decode_results.append(result["decoded"])
        
        # All decode results should be identical
        assert len(set(decode_results)) == 1
        assert decode_results[0] == text
    
    def test_large_text_handling(self):
        """Test handling of large text."""
        # Create a large text (1KB)
        large_text = "A" * 1024
        
        # Should encode without issues
        encode_result = self.utility.encode(large_text)
        assert encode_result["original_length"] == 1024
        assert encode_result["is_valid_base64"] is True
        
        # Should decode back correctly
        decode_result = self.utility.decode(encode_result["encoded"])
        assert decode_result["decoded"] == large_text
        assert decode_result["decoded_length"] == 1024
    
    def test_special_characters_handling(self):
        """Test handling of special characters."""
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        
        encode_result = self.utility.encode(special_chars)
        decode_result = self.utility.decode(encode_result["encoded"])
        
        assert decode_result["decoded"] == special_chars
