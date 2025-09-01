"""Tests for HashGenerator class.

This module contains comprehensive tests for the HashGenerator class,
testing various hashing algorithms, error handling, and edge cases.
"""

import pytest
import hashlib
from src.core.generators.hash_generator import HashGenerator


class TestHashGenerator:
    
    def setup_method(self):
        """Setup for each test method."""
        self.generator = HashGenerator()
    
    def test_generate_hash_default(self):
        """Test default hash generation (SHA256)."""
        result = self.generator.generate_hash("hello world")
        
        assert "hash" in result
        assert "algorithm" in result
        assert "input_text" in result
        assert "input_length" in result
        assert "hash_length" in result
        assert "encoding" in result
        
        assert result["algorithm"] == "sha256"
        assert result["input_text"] == "hello world"
        assert result["input_length"] == 11
        assert result["hash_length"] == 64  # SHA256 produces 64 hex chars
        assert result["encoding"] == "utf-8"
        
        # Verify actual hash value
        expected_hash = hashlib.sha256("hello world".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_md5(self):
        """Test MD5 hash generation."""
        result = self.generator.generate_hash("test", "md5")
        
        assert result["algorithm"] == "md5"
        assert result["hash_length"] == 32  # MD5 produces 32 hex chars
        
        # Verify actual hash value
        expected_hash = hashlib.md5("test".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_sha1(self):
        """Test SHA1 hash generation."""
        result = self.generator.generate_hash("test", "sha1")
        
        assert result["algorithm"] == "sha1"
        assert result["hash_length"] == 40  # SHA1 produces 40 hex chars
        
        # Verify actual hash value
        expected_hash = hashlib.sha1("test".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_sha512(self):
        """Test SHA512 hash generation."""
        result = self.generator.generate_hash("test", "sha512")
        
        assert result["algorithm"] == "sha512"
        assert result["hash_length"] == 128  # SHA512 produces 128 hex chars
        
        # Verify actual hash value
        expected_hash = hashlib.sha512("test".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_sha3_256(self):
        """Test SHA3-256 hash generation."""
        result = self.generator.generate_hash("test", "sha3_256")
        
        assert result["algorithm"] == "sha3_256"
        assert result["hash_length"] == 64  # SHA3-256 produces 64 hex chars
        
        # Verify actual hash value
        expected_hash = hashlib.sha3_256("test".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_blake2b(self):
        """Test BLAKE2b hash generation."""
        result = self.generator.generate_hash("test", "blake2b")
        
        assert result["algorithm"] == "blake2b"
        assert result["hash_length"] == 128  # BLAKE2b produces 128 hex chars by default
        
        # Verify actual hash value
        expected_hash = hashlib.blake2b("test".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_blake2s(self):
        """Test BLAKE2s hash generation."""
        result = self.generator.generate_hash("test", "blake2s")
        
        assert result["algorithm"] == "blake2s"
        assert result["hash_length"] == 64  # BLAKE2s produces 64 hex chars by default
        
        # Verify actual hash value
        expected_hash = hashlib.blake2s("test".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_case_insensitive(self):
        """Test that algorithm names are case insensitive."""
        result1 = self.generator.generate_hash("test", "SHA256")
        result2 = self.generator.generate_hash("test", "sha256")
        result3 = self.generator.generate_hash("test", "Sha256")
        
        assert result1["hash"] == result2["hash"] == result3["hash"]
        assert result1["algorithm"] == result2["algorithm"] == result3["algorithm"] == "sha256"
    
    def test_generate_hash_whitespace_handling(self):
        """Test that algorithm names handle whitespace."""
        result1 = self.generator.generate_hash("test", " sha256 ")
        result2 = self.generator.generate_hash("test", "sha256")
        
        assert result1["hash"] == result2["hash"]
        assert result1["algorithm"] == result2["algorithm"] == "sha256"
    
    def test_generate_hash_empty_string(self):
        """Test hash generation with empty string."""
        result = self.generator.generate_hash("", "sha256")
        
        assert result["input_text"] == ""
        assert result["input_length"] == 0
        assert result["hash_length"] == 64
        
        # Verify actual hash value for empty string
        expected_hash = hashlib.sha256("".encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_unicode_text(self):
        """Test hash generation with Unicode text."""
        unicode_text = "Hello 世界! 🌍"
        result = self.generator.generate_hash(unicode_text, "sha256")
        
        assert result["input_text"] == unicode_text
        assert result["input_length"] == len(unicode_text)
        assert result["encoding"] == "utf-8"
        
        # Verify actual hash value
        expected_hash = hashlib.sha256(unicode_text.encode('utf-8')).hexdigest()
        assert result["hash"] == expected_hash
    
    def test_generate_hash_invalid_algorithm(self):
        """Test hash generation with invalid algorithm."""
        with pytest.raises(ValueError, match="Unsupported algorithm: invalid"):
            self.generator.generate_hash("test", "invalid")
    
    def test_generate_hash_non_string_input(self):
        """Test hash generation with non-string input."""
        with pytest.raises(ValueError, match="Text must be a string"):
            self.generator.generate_hash(123, "sha256")
        
        with pytest.raises(ValueError, match="Text must be a string"):
            self.generator.generate_hash(None, "sha256")
        
        with pytest.raises(ValueError, match="Text must be a string"):
            self.generator.generate_hash([], "sha256")
    
    def test_generate_multiple_hashes_default(self):
        """Test multiple hash generation with default algorithms."""
        result = self.generator.generate_multiple_hashes("test")
        
        assert "hashes" in result
        assert "input_text" in result
        assert "input_length" in result
        assert "algorithms_used" in result
        assert "encoding" in result
        
        assert result["input_text"] == "test"
        assert result["input_length"] == 4
        assert result["encoding"] == "utf-8"
        
        # Check default algorithms
        expected_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        assert result["algorithms_used"] == expected_algorithms
        
        # Verify each hash
        for algorithm in expected_algorithms:
            assert algorithm in result["hashes"]
            assert "hash" in result["hashes"][algorithm]
            assert "hash_length" in result["hashes"][algorithm]
    
    def test_generate_multiple_hashes_custom_algorithms(self):
        """Test multiple hash generation with custom algorithms."""
        algorithms = ['sha256', 'sha3_256', 'blake2b']
        result = self.generator.generate_multiple_hashes("test", algorithms)
        
        assert result["algorithms_used"] == algorithms
        
        # Verify each hash
        for algorithm in algorithms:
            assert algorithm in result["hashes"]
            assert "hash" in result["hashes"][algorithm]
            assert "hash_length" in result["hashes"][algorithm]
    
    def test_generate_multiple_hashes_with_invalid_algorithm(self):
        """Test multiple hash generation with some invalid algorithms."""
        algorithms = ['sha256', 'invalid', 'md5']
        result = self.generator.generate_multiple_hashes("test", algorithms)
        
        # Valid algorithms should work
        assert "hash" in result["hashes"]["sha256"]
        assert "hash" in result["hashes"]["md5"]
        
        # Invalid algorithm should have error
        assert "error" in result["hashes"]["invalid"]
        assert "Unsupported algorithm" in result["hashes"]["invalid"]["error"]
    
    def test_supported_algorithms_list(self):
        """Test that all supported algorithms are accessible."""
        supported = self.generator.SUPPORTED_ALGORITHMS
        
        # Check that common algorithms are supported
        expected_algorithms = [
            'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
            'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
            'blake2b', 'blake2s'
        ]
        
        for algorithm in expected_algorithms:
            assert algorithm in supported
            assert callable(supported[algorithm])
    
    def test_hash_consistency(self):
        """Test that same input produces same hash consistently."""
        text = "consistency test"
        algorithm = "sha256"
        
        # Generate hash multiple times
        results = []
        for _ in range(5):
            result = self.generator.generate_hash(text, algorithm)
            results.append(result["hash"])
        
        # All results should be identical
        assert len(set(results)) == 1
    
    def test_hash_different_inputs(self):
        """Test that different inputs produce different hashes."""
        algorithm = "sha256"
        
        hash1 = self.generator.generate_hash("input1", algorithm)["hash"]
        hash2 = self.generator.generate_hash("input2", algorithm)["hash"]
        hash3 = self.generator.generate_hash("input1 ", algorithm)["hash"]  # With space
        
        # All hashes should be different
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3
    
    def test_algorithm_info_method(self):
        """Test get_algorithm_info method."""
        # Test specific algorithm info
        info = self.generator.get_algorithm_info("sha256")

        assert isinstance(info, dict)
        assert "algorithm" in info
        assert "output_size_hex" in info
        assert "security_level" in info
        assert "description" in info
        assert "family" in info

        assert info["algorithm"] == "sha256"
        assert info["output_size_hex"] == 64
        assert info["security_level"] == "good"
        assert "SHA-2" in info["description"]
        assert info["family"] == "SHA-2"

    def test_algorithm_info_invalid_algorithm(self):
        """Test get_algorithm_info with invalid algorithm."""
        with pytest.raises(ValueError, match="Unsupported algorithm: invalid"):
            self.generator.get_algorithm_info("invalid")

    def test_get_supported_algorithms_method(self):
        """Test get_supported_algorithms method."""
        algorithms = self.generator.get_supported_algorithms()

        assert isinstance(algorithms, list)
        assert len(algorithms) > 0

        # Check that common algorithms are supported
        expected_algorithms = [
            'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
            'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
            'blake2b', 'blake2s'
        ]

        for algorithm in expected_algorithms:
            assert algorithm in algorithms
