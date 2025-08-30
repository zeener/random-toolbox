import pytest
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.core.generators.password_generator import PasswordGenerator


class TestPasswordGenerator:
    
    def setup_method(self):
        """Setup for each test method."""
        self.generator = PasswordGenerator()
    
    def test_generate_password_default(self):
        """Test default password generation."""
        result = self.generator.generate_password()
        
        assert "password" in result
        assert "length" in result
        assert "entropy_bits" in result
        assert "strength" in result
        
        password = result["password"]
        assert len(password) == 16
        assert isinstance(password, str)
    
    def test_generate_password_custom_length(self):
        """Test password generation with custom length."""
        result = self.generator.generate_password(length=12)
        assert result["length"] == 12
        assert len(result["password"]) == 12
        
        result = self.generator.generate_password(length=24)
        assert result["length"] == 24
        assert len(result["password"]) == 24
    
    def test_generate_password_invalid_length(self):
        """Test password generation with invalid lengths."""
        with pytest.raises(ValueError, match="Password length must be between 8 and 128"):
            self.generator.generate_password(length=7)
            
        with pytest.raises(ValueError, match="Password length must be between 8 and 128"):
            self.generator.generate_password(length=129)
    
    def test_character_set_options(self):
        """Test different character set combinations."""
        # Only uppercase
        result = self.generator.generate_password(
            length=20, uppercase=True, lowercase=False, numbers=False, symbols=False
        )
        password = result["password"]
        assert all(c.isupper() for c in password)
        
        # Only lowercase
        result = self.generator.generate_password(
            length=20, uppercase=False, lowercase=True, numbers=False, symbols=False
        )
        password = result["password"]
        assert all(c.islower() for c in password)
        
        # Only numbers
        result = self.generator.generate_password(
            length=20, uppercase=False, lowercase=False, numbers=True, symbols=False
        )
        password = result["password"]
        assert all(c.isdigit() for c in password)
    
    def test_symbols_inclusion(self):
        """Test symbol inclusion in passwords."""
        result = self.generator.generate_password(
            length=50, symbols=True
        )
        password = result["password"]
        
        # Should contain at least one symbol
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        assert any(c in symbols for c in password)
    
    def test_exclude_ambiguous_characters(self):
        """Test exclusion of ambiguous characters."""
        result = self.generator.generate_password(
            length=100, exclude_ambiguous=True
        )
        password = result["password"]
        
        ambiguous = "0O1lI|`'"
        assert not any(c in ambiguous for c in password)
    
    def test_entropy_calculation(self):
        """Test entropy calculation accuracy."""
        # Test with known parameters
        result = self.generator.generate_password(
            length=10, uppercase=True, lowercase=True, numbers=True, symbols=False
        )
        
        # Charset: 26 + 26 + 10 = 62 characters
        # Entropy = 10 * log2(62) ≈ 59.54 bits
        import math
        expected_entropy = 10 * math.log2(62)  # ≈ 59.54 bits
        assert 55 < result["entropy_bits"] < 65  # Allow reasonable range
    
    def test_strength_assessment(self):
        """Test password strength assessment."""
        # Very weak password
        result = self.generator.generate_password(length=8, uppercase=False, lowercase=True, numbers=False, symbols=False)
        assert result["strength"] in ["weak", "very_weak"]
        
        # Strong password
        result = self.generator.generate_password(length=20, symbols=True)
        assert result["strength"] in ["strong", "very_strong"]
    
    def test_config_in_result(self):
        """Test that config is included in result."""
        result = self.generator.generate_password(
            uppercase=True, lowercase=False, numbers=True, symbols=True, exclude_ambiguous=True
        )
        
        config = result["config"]
        assert config["uppercase"] is True
        assert config["lowercase"] is False
        assert config["numbers"] is True
        assert config["symbols"] is True
        assert config["exclude_ambiguous"] is True
    
    def test_no_character_types_enabled(self):
        """Test error when no character types are enabled."""
        with pytest.raises(ValueError, match="At least one character type must be enabled"):
            self.generator.generate_password(
                uppercase=False, lowercase=False, numbers=False, symbols=False
            )
    
    def test_generate_multiple_passwords(self):
        """Test generating multiple passwords."""
        results = self.generator.generate_multiple(count=3, length=12)
        
        assert len(results) == 3
        assert all("password" in result for result in results)
        assert all(len(result["password"]) == 12 for result in results)
        
        # Should be different passwords
        passwords = [result["password"] for result in results]
        assert len(set(passwords)) == 3  # All unique
    
    def test_generate_multiple_invalid_count(self):
        """Test generating multiple passwords with invalid count."""
        with pytest.raises(ValueError, match="Count must be between 1 and 100"):
            self.generator.generate_multiple(count=0)
            
        with pytest.raises(ValueError, match="Count must be between 1 and 100"):
            self.generator.generate_multiple(count=101)
    
    def test_requirement_enforcement(self):
        """Test that generated passwords meet all requirements."""
        result = self.generator.generate_password(
            length=50,  # Large length to ensure requirement satisfaction
            uppercase=True,
            lowercase=True,
            numbers=True,
            symbols=True,
            ensure_requirements=True
        )
        
        password = result["password"]
        
        # Check that all required character types are present
        assert any(c.isupper() for c in password), "Missing uppercase characters"
        assert any(c.islower() for c in password), "Missing lowercase characters"
        assert any(c.isdigit() for c in password), "Missing numbers"
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password), "Missing symbols"
    
    def test_randomness_quality(self):
        """Test quality of randomness."""
        # Generate many passwords and check for patterns
        passwords = []
        for _ in range(100):
            result = self.generator.generate_password(length=16)
            passwords.append(result["password"])
        
        # All should be unique
        assert len(set(passwords)) == 100
        
        # Check character distribution (should be reasonably balanced)
        all_chars = "".join(passwords)
        char_counts = {}
        for char in all_chars:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Should have reasonable character variety
        assert len(char_counts) > 30  # At least 30 different characters used
    
    def test_charset_building(self):
        """Test internal charset building method."""
        # Test with all options enabled
        charset = self.generator._build_charset(
            uppercase=True, lowercase=True, numbers=True, symbols=True, exclude_ambiguous=False
        )
        assert len(charset) > 85  # Should be quite large
        
        # Test with ambiguous exclusion
        charset = self.generator._build_charset(
            uppercase=True, lowercase=True, numbers=True, symbols=False, exclude_ambiguous=True
        )
        ambiguous = "0O1lI|`'"
        assert not any(c in ambiguous for c in charset)
    
    def test_ensure_requirements_method(self):
        """Test internal requirement checking method."""
        # Test password that meets requirements
        config = {'uppercase': True, 'lowercase': True, 'numbers': True, 'symbols': False}
        assert self.generator._ensure_requirements("Abc123def", config) is True
        
        # Test password missing uppercase
        assert self.generator._ensure_requirements("abc123def", config) is False
        
        # Test password missing numbers
        config = {'uppercase': False, 'lowercase': True, 'numbers': True, 'symbols': False}
        assert self.generator._ensure_requirements("abcdefgh", config) is False