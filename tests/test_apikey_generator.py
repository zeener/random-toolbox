import pytest
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.core.generators.apikey_generator import APIKeyGenerator


class TestAPIKeyGenerator:
    
    def setup_method(self):
        """Setup for each test method."""
        self.generator = APIKeyGenerator()
    
    def test_generate_hex_default(self):
        """Test default hex key generation."""
        key = self.generator.generate_hex()
        assert len(key) == 64  # 32 bytes = 64 hex chars
        assert re.match(r'^[0-9a-f]+$', key)  # Only hex characters
    
    def test_generate_hex_custom_length(self):
        """Test hex generation with custom length."""
        key = self.generator.generate_hex(16)
        assert len(key) == 32  # 16 bytes = 32 hex chars
        
        key = self.generator.generate_hex(8)
        assert len(key) == 16  # 8 bytes = 16 hex chars
    
    def test_generate_hex_invalid_length(self):
        """Test hex generation with invalid lengths."""
        with pytest.raises(ValueError, match="Length must be between 1 and 128"):
            self.generator.generate_hex(0)
            
        with pytest.raises(ValueError, match="Length must be between 1 and 128"):
            self.generator.generate_hex(129)
    
    def test_generate_base64_default(self):
        """Test default base64 key generation."""
        key = self.generator.generate_base64()
        assert len(key) == 32  # 24 bytes ≈ 32 base64 chars
        assert re.match(r'^[A-Za-z0-9_-]+$', key)  # URL-safe base64
    
    def test_generate_base64_custom_length(self):
        """Test base64 generation with custom length."""
        key = self.generator.generate_base64(16)
        # 16 bytes ≈ 22-24 base64 chars (depending on padding)
        assert 20 <= len(key) <= 25
    
    def test_generate_base58_default(self):
        """Test default base58 key generation."""
        key = self.generator.generate_base58()
        assert len(key) > 40  # 32 bytes ≈ 44+ base58 chars
        
        # Should not contain ambiguous characters
        ambiguous = "0OIl"
        assert not any(c in ambiguous for c in key)
        
        # Should only contain base58 alphabet
        base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        assert all(c in base58_alphabet for c in key)
    
    def test_generate_custom_default(self):
        """Test custom generation with default charset."""
        key = self.generator.generate_custom()
        assert len(key) == 32
        assert re.match(r'^[A-Za-z0-9]+$', key)  # Letters and numbers only
    
    def test_generate_custom_charset(self):
        """Test custom generation with custom charset."""
        charset = "ABCDEF123456"
        key = self.generator.generate_custom(length=20, charset=charset)
        
        assert len(key) == 20
        assert all(c in charset for c in key)
    
    def test_generate_custom_invalid_params(self):
        """Test custom generation with invalid parameters."""
        with pytest.raises(ValueError, match="Length must be between 1 and 256"):
            self.generator.generate_custom(length=0)
            
        with pytest.raises(ValueError, match="Length must be between 1 and 256"):
            self.generator.generate_custom(length=257)
            
        with pytest.raises(ValueError, match="Charset must contain at least 2 characters"):
            self.generator.generate_custom(charset="A")
    
    def test_generate_main_method_hex(self):
        """Test main generate method with hex format."""
        result = self.generator.generate(key_format="hex", length=16)
        
        assert "api_key" in result
        assert "format" in result
        assert "entropy_bits" in result
        assert "security_level" in result
        
        assert result["format"] == "hex"
        assert result["length"] == 32  # Actual hex string length
        assert len(result["api_key"]) == 32  # 16 bytes = 32 hex chars
    
    def test_generate_main_method_base64(self):
        """Test main generate method with base64 format."""
        result = self.generator.generate(key_format="base64", length=24)
        
        assert result["format"] == "base64"
        assert result["length"] == 32  # This is the actual output length from base64
        assert re.match(r'^[A-Za-z0-9_-]+$', result["api_key"])
    
    def test_generate_main_method_base58(self):
        """Test main generate method with base58 format."""
        result = self.generator.generate(key_format="base58", length=16)
        
        assert result["format"] == "base58"
        assert result["length"] > 16  # base58 encoding produces longer strings
        
        # Should not contain ambiguous characters
        ambiguous = "0OIl"
        assert not any(c in ambiguous for c in result["api_key"])
    
    def test_generate_with_prefix(self):
        """Test key generation with prefix."""
        prefix = "sk_"
        result = self.generator.generate(key_format="hex", length=16, prefix=prefix)
        
        assert result["api_key"].startswith(prefix)
        assert result["prefix"] == prefix
        assert result["total_length"] == len(result["api_key"])
        assert result["total_length"] > result["length"]
    
    def test_generate_invalid_prefix(self):
        """Test key generation with invalid prefix."""
        with pytest.raises(ValueError, match="Prefix cannot exceed 20 characters"):
            self.generator.generate(prefix="a" * 21)
    
    def test_generate_invalid_format(self):
        """Test key generation with invalid format."""
        with pytest.raises(ValueError, match="Invalid format"):
            self.generator.generate(key_format="invalid")
    
    def test_entropy_calculation(self):
        """Test entropy calculation for different formats."""
        # Hex: 4 bits per character
        result = self.generator.generate(key_format="hex", length=16)
        expected_entropy = 16 * 4  # 64 bits
        assert abs(result["entropy_bits"] - expected_entropy) < 1
        
        # Base64: ~6 bits per character  
        result = self.generator.generate(key_format="base64", length=16)
        expected_entropy = 16 * 6  # ~96 bits
        assert abs(result["entropy_bits"] - expected_entropy) < 10
    
    def test_security_level_assessment(self):
        """Test security level assessment."""
        # Test different entropy levels
        assert self.generator._assess_security(300) == "military_grade"
        assert self.generator._assess_security(150) == "very_strong"
        assert self.generator._assess_security(100) == "strong"
        assert self.generator._assess_security(70) == "adequate"
        assert self.generator._assess_security(30) == "weak"
    
    def test_generate_multiple_keys(self):
        """Test generating multiple API keys."""
        results = self.generator.generate_multiple(count=3, key_format="hex", length=16)
        
        assert len(results) == 3
        assert all("api_key" in result for result in results)
        assert all(result["format"] == "hex" for result in results)
        
        # All should be different
        keys = [result["api_key"] for result in results]
        assert len(set(keys)) == 3
    
    def test_generate_multiple_invalid_count(self):
        """Test generating multiple keys with invalid count."""
        with pytest.raises(ValueError, match="Count must be between 1 and 50"):
            self.generator.generate_multiple(count=0)
            
        with pytest.raises(ValueError, match="Count must be between 1 and 50"):
            self.generator.generate_multiple(count=51)
    
    def test_randomness_quality(self):
        """Test quality of randomness across multiple generations."""
        keys = []
        for _ in range(50):
            result = self.generator.generate(key_format="hex", length=32)
            keys.append(result["api_key"])
        
        # All should be unique
        assert len(set(keys)) == 50
        
        # Check character distribution
        all_chars = "".join(keys)
        char_counts = {}
        for char in all_chars:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Should use all hex characters reasonably
        hex_chars = "0123456789abcdef"
        used_chars = set(char_counts.keys())
        assert len(used_chars.intersection(hex_chars)) >= 14  # Most hex chars should appear
    
    def test_base58_no_leading_zeros(self):
        """Test that base58 handles leading zeros correctly."""
        # This is a bit tricky to test deterministically, but we can check format
        for _ in range(10):
            key = self.generator.generate_base58(32)
            # Should be valid base58
            base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
            assert all(c in base58_alphabet for c in key)
    
    def test_custom_format_edge_cases(self):
        """Test custom format with edge cases."""
        # Very small charset
        result = self.generator.generate(key_format="custom", length=10, charset="AB")
        password = result["api_key"]
        assert len(password) == 10
        assert all(c in "AB" for c in password)
        
        # Large charset
        charset = "".join(chr(i) for i in range(33, 127))  # All printable ASCII
        result = self.generator.generate(key_format="custom", length=20, charset=charset)
        assert len(result["api_key"]) == 20