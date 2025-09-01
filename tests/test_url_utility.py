"""Tests for URLUtility class.

This module contains comprehensive tests for the URLUtility class,
testing URL encoding, decoding, validation, and various edge cases.
"""

import pytest
import urllib.parse
from src.core.utilities.url_utility import URLUtility


class TestURLUtility:
    
    def setup_method(self):
        """Setup for each test method."""
        self.utility = URLUtility()
    
    def test_encode_simple_text(self):
        """Test encoding simple text with special characters."""
        result = self.utility.encode("Hello World! @#$%", "standard")
        
        assert "encoded" in result
        assert "original_text" in result
        assert "original_length" in result
        assert "encoded_length" in result
        assert "size_increase_percent" in result
        assert "encoding_type" in result
        assert "characters_encoded" in result
        
        assert result["original_text"] == "Hello World! @#$%"
        assert result["original_length"] == 17
        assert result["encoding_type"] == "standard"
        
        # Verify actual encoding
        expected = urllib.parse.quote("Hello World! @#$%")
        assert result["encoded"] == expected
        assert result["encoded"] == "Hello%20World%21%20%40%23%24%25"
    
    def test_encode_standard_type(self):
        """Test standard URL encoding."""
        text = "Hello World! @#$%^&*()"
        result = self.utility.encode(text, "standard")
        
        assert result["encoding_type"] == "standard"
        expected = urllib.parse.quote(text)
        assert result["encoded"] == expected
    
    def test_encode_plus_type(self):
        """Test plus URL encoding (spaces become +)."""
        text = "Hello World! @#$%"
        result = self.utility.encode(text, "plus")
        
        assert result["encoding_type"] == "plus"
        expected = urllib.parse.quote_plus(text)
        assert result["encoded"] == expected
        
        # Verify spaces become +
        assert "%20" not in result["encoded"]
        assert "+" in result["encoded"]
    
    def test_encode_default_type(self):
        """Test encoding with default type (should be standard)."""
        text = "Hello World!"
        result = self.utility.encode(text)
        
        assert result["encoding_type"] == "standard"
        expected = urllib.parse.quote(text)
        assert result["encoded"] == expected
    
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
    
    def test_encode_invalid_type(self):
        """Test encoding with invalid type raises error."""
        with pytest.raises(ValueError, match="Encoding type must be one of: 'standard', 'plus', 'component'"):
            self.utility.encode("test", "invalid")
    
    def test_encode_unicode_text(self):
        """Test encoding Unicode text."""
        unicode_text = "Hello 世界! 🌍"
        result = self.utility.encode(unicode_text, "standard")
        
        assert result["original_text"] == unicode_text
        assert result["original_length"] == len(unicode_text)
        
        # Verify actual encoding
        expected = urllib.parse.quote(unicode_text)
        assert result["encoded"] == expected
    
    def test_encode_characters_encoded_count(self):
        """Test counting of encoded characters."""
        # Text with known special characters
        text = "Hello World! @#$"  # Space, !, @, #, $ should be encoded
        result = self.utility.encode(text, "standard")
        
        # Count characters that should be encoded
        special_chars = " !@#$"
        expected_count = sum(1 for char in text if char in special_chars)
        assert result["characters_encoded"] == expected_count
    
    def test_encode_size_calculation(self):
        """Test size increase calculation."""
        text = "Hello World!"
        result = self.utility.encode(text, "standard")
        
        original_size = result["original_length"]
        encoded_size = result["encoded_length"]
        size_increase = result["size_increase_percent"]
        
        expected_increase = ((encoded_size - original_size) / original_size) * 100
        assert abs(size_increase - expected_increase) < 0.01
    
    def test_encode_no_special_characters(self):
        """Test encoding text with no special characters."""
        text = "HelloWorld123"  # No characters that need encoding
        result = self.utility.encode(text, "standard")
        
        assert result["encoded"] == text  # Should be unchanged
        assert result["characters_encoded"] == 0
        assert result["size_increase_percent"] == 0.0
    
    def test_decode_simple_text(self):
        """Test decoding simple URL-encoded text."""
        encoded_text = "Hello%20World%21%20%40%23%24%25"
        result = self.utility.decode(encoded_text, "standard")

        assert "decoded" in result
        assert "original_encoded" in result
        assert "encoded_length" in result
        assert "decoded_length" in result
        assert "size_decrease_percent" in result
        assert "decoding_type" in result
        assert "characters_decoded" in result

        assert result["decoded"] == "Hello World! @#$%"
        assert result["original_encoded"] == encoded_text
        assert result["encoded_length"] == len(encoded_text)
        assert result["decoded_length"] == 17
        assert result["decoding_type"] == "standard"
    
    def test_decode_standard_type(self):
        """Test standard URL decoding."""
        encoded_text = "Hello%20World%21"
        result = self.utility.decode(encoded_text, "standard")
        
        assert result["decoding_type"] == "standard"
        expected = urllib.parse.unquote(encoded_text)
        assert result["decoded"] == expected
        assert result["decoded"] == "Hello World!"
    
    def test_decode_plus_type(self):
        """Test plus URL decoding (+ becomes space)."""
        encoded_text = "Hello+World%21"
        result = self.utility.decode(encoded_text, "plus")
        
        assert result["decoding_type"] == "plus"
        expected = urllib.parse.unquote_plus(encoded_text)
        assert result["decoded"] == expected
        assert result["decoded"] == "Hello World!"
    
    def test_decode_default_type(self):
        """Test decoding with default type (should be standard)."""
        encoded_text = "Hello%20World"
        result = self.utility.decode(encoded_text)
        
        assert result["decoding_type"] == "standard"
        expected = urllib.parse.unquote(encoded_text)
        assert result["decoded"] == expected
    
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
    
    def test_decode_invalid_type(self):
        """Test decoding with invalid type raises error."""
        with pytest.raises(ValueError, match="Decoding type must be one of: 'standard', 'plus', 'auto'"):
            self.utility.decode("test", "invalid")
    
    def test_decode_whitespace_handling(self):
        """Test decoding handles whitespace."""
        encoded_text = "Hello%20World"
        encoded_with_whitespace = f"  {encoded_text}  "

        result = self.utility.decode(encoded_with_whitespace, "standard")
        # URL utility doesn't trim whitespace like Base64 utility does
        assert result["decoded"] == "  Hello World  "
        assert result["original_encoded"] == encoded_with_whitespace
    
    def test_decode_unicode_text(self):
        """Test decoding Unicode text."""
        # First encode Unicode text
        unicode_text = "Hello 世界! 🌍"
        encoded = urllib.parse.quote(unicode_text)
        
        # Then decode it
        result = self.utility.decode(encoded, "standard")
        assert result["decoded"] == unicode_text
    
    def test_decode_characters_decoded_count(self):
        """Test counting of decoded characters."""
        encoded_text = "Hello%20World%21%20%40"  # %20, %21, %20, %40 = 4 encoded sequences
        result = self.utility.decode(encoded_text, "standard")
        
        # Count %XX sequences
        encoded_sequences = encoded_text.count('%')
        assert result["characters_decoded"] == encoded_sequences
    
    def test_decode_size_calculation(self):
        """Test size decrease calculation."""
        encoded_text = "Hello%20World%21"
        result = self.utility.decode(encoded_text, "standard")
        
        encoded_size = result["encoded_length"]
        decoded_size = result["decoded_length"]
        size_decrease = result["size_decrease_percent"]
        
        expected_decrease = ((encoded_size - decoded_size) / encoded_size) * 100
        assert abs(size_decrease - expected_decrease) < 0.01
    
    def test_decode_no_encoded_characters(self):
        """Test decoding text with no encoded characters."""
        text = "HelloWorld123"  # No %XX sequences
        result = self.utility.decode(text, "standard")
        
        assert result["decoded"] == text  # Should be unchanged
        assert result["characters_decoded"] == 0
        assert result["size_decrease_percent"] == 0.0
    
    def test_validate_valid_url_encoded(self):
        """Test validation of valid URL-encoded strings."""
        valid_strings = [
            "Hello%20World",
            "test%21%40%23",
            "HelloWorld",  # No encoding needed
            "test+string",  # Plus encoding
            "file%2Epath%2Etxt",
        ]
        
        for valid_string in valid_strings:
            result = self.utility.validate(valid_string)
            assert result["is_valid"] is True
            assert "error" not in result or result["error"] is None
    
    def test_validate_invalid_url_encoded(self):
        """Test validation of invalid URL-encoded strings."""
        invalid_strings = [
            "test%2",      # Incomplete encoding
            "test%GG",     # Invalid hex characters
            "test%",       # Incomplete at end
            "test%2G",     # Invalid hex character
        ]

        for invalid_string in invalid_strings:
            result = self.utility.validate(invalid_string)
            assert result["is_valid"] is False
            assert "issues" in result
            assert "suggestions" in result
    
    def test_validate_non_string_input(self):
        """Test validation of non-string input."""
        result = self.utility.validate(123)
        assert result["is_valid"] is False
        assert result["error"] == "Input must be a string"
        assert "suggestions" in result
    
    def test_encode_decode_roundtrip_standard(self):
        """Test that encoding then decoding returns original text (standard)."""
        test_strings = [
            "Hello World!",
            "test@example.com",
            "path/to/file.txt",
            "Hello 世界! 🌍",
            "query=value&param=test",
            "!@#$%^&*()_+-=[]{}|;:,.<>?",
        ]
        
        for original_text in test_strings:
            # Encode
            encode_result = self.utility.encode(original_text, "standard")
            encoded_text = encode_result["encoded"]
            
            # Decode
            decode_result = self.utility.decode(encoded_text, "standard")
            decoded_text = decode_result["decoded"]
            
            # Should match original
            assert decoded_text == original_text
    
    def test_encode_decode_roundtrip_plus(self):
        """Test that encoding then decoding returns original text (plus)."""
        test_strings = [
            "Hello World!",
            "form data with spaces",
            "test+already+plus",
        ]
        
        for original_text in test_strings:
            # Encode
            encode_result = self.utility.encode(original_text, "plus")
            encoded_text = encode_result["encoded"]
            
            # Decode
            decode_result = self.utility.decode(encoded_text, "plus")
            decoded_text = decode_result["decoded"]
            
            # Should match original
            assert decoded_text == original_text
    
    def test_multiple_operations_consistency(self):
        """Test that multiple operations on same input are consistent."""
        text = "Hello World! @#$%"
        
        # Encode multiple times
        results = []
        for _ in range(5):
            result = self.utility.encode(text, "standard")
            results.append(result["encoded"])
        
        # All results should be identical
        assert len(set(results)) == 1
        
        # Decode multiple times
        encoded = results[0]
        decode_results = []
        for _ in range(5):
            result = self.utility.decode(encoded, "standard")
            decode_results.append(result["decoded"])
        
        # All decode results should be identical
        assert len(set(decode_results)) == 1
        assert decode_results[0] == text
    
    def test_special_url_characters(self):
        """Test handling of special URL characters."""
        # Characters that have special meaning in URLs
        special_chars = "?&=+%#/"
        
        encode_result = self.utility.encode(special_chars, "standard")
        decode_result = self.utility.decode(encode_result["encoded"], "standard")
        
        assert decode_result["decoded"] == special_chars
    
    def test_large_text_handling(self):
        """Test handling of large text."""
        # Create a large text with special characters
        large_text = "Hello World! @#$% " * 100  # Repeat to make it large
        
        # Should encode without issues
        encode_result = self.utility.encode(large_text, "standard")
        assert encode_result["original_length"] == len(large_text)
        
        # Should decode back correctly
        decode_result = self.utility.decode(encode_result["encoded"], "standard")
        assert decode_result["decoded"] == large_text
    
    def test_edge_case_percent_signs(self):
        """Test handling of literal percent signs."""
        text = "100% complete"
        
        encode_result = self.utility.encode(text, "standard")
        decode_result = self.utility.decode(encode_result["encoded"], "standard")
        
        assert decode_result["decoded"] == text
