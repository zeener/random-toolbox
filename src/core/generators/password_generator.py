import secrets
import string
import math
from typing import Set


class PasswordGenerator:
    
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase  
    NUMBERS = string.digits
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ambiguous characters that can be easily confused
    AMBIGUOUS_CHARS = "0O1lI|`'"
    
    def __init__(self):
        pass
    
    def _build_charset(self, 
                      uppercase: bool = True,
                      lowercase: bool = True, 
                      numbers: bool = True,
                      symbols: bool = False,
                      exclude_ambiguous: bool = False) -> str:
        """Build character set based on options."""
        
        charset = ""
        
        if uppercase:
            charset += self.UPPERCASE
        if lowercase:
            charset += self.LOWERCASE
        if numbers:
            charset += self.NUMBERS
        if symbols:
            charset += self.SYMBOLS
            
        if exclude_ambiguous:
            charset = "".join(c for c in charset if c not in self.AMBIGUOUS_CHARS)
            
        if not charset:
            raise ValueError("At least one character type must be enabled")
            
        return charset
    
    def _calculate_entropy(self, length: int, charset_size: int) -> float:
        """Calculate password entropy in bits."""
        return length * math.log2(charset_size)
    
    def _ensure_requirements(self, password: str, charset_config: dict) -> bool:
        """Ensure password meets all requirements."""
        
        if charset_config.get('uppercase', False):
            if not any(c in self.UPPERCASE for c in password):
                return False
                
        if charset_config.get('lowercase', False):
            if not any(c in self.LOWERCASE for c in password):
                return False
                
        if charset_config.get('numbers', False):
            if not any(c in self.NUMBERS for c in password):
                return False
                
        if charset_config.get('symbols', False):
            if not any(c in self.SYMBOLS for c in password):
                return False
                
        return True
    
    def generate_password(self,
                         length: int = 16,
                         uppercase: bool = True,
                         lowercase: bool = True,
                         numbers: bool = True, 
                         symbols: bool = False,
                         exclude_ambiguous: bool = False,
                         ensure_requirements: bool = True) -> dict:
        """Generate a secure random password with specified requirements."""
        
        if length < 8 or length > 128:
            raise ValueError("Password length must be between 8 and 128 characters")
            
        charset = self._build_charset(uppercase, lowercase, numbers, symbols, exclude_ambiguous)
        charset_config = {
            'uppercase': uppercase,
            'lowercase': lowercase, 
            'numbers': numbers,
            'symbols': symbols
        }
        
        max_attempts = 100
        for attempt in range(max_attempts):
            password = "".join(secrets.choice(charset) for _ in range(length))
            
            if not ensure_requirements or self._ensure_requirements(password, charset_config):
                entropy = self._calculate_entropy(length, len(charset))
                
                return {
                    "password": password,
                    "length": length,
                    "entropy_bits": round(entropy, 2),
                    "charset_size": len(charset),
                    "strength": self._assess_strength(entropy),
                    "config": {
                        "uppercase": uppercase,
                        "lowercase": lowercase,
                        "numbers": numbers,
                        "symbols": symbols,
                        "exclude_ambiguous": exclude_ambiguous
                    }
                }
        
        raise RuntimeError(f"Failed to generate password meeting requirements after {max_attempts} attempts")
    
    def _assess_strength(self, entropy: float) -> str:
        """Assess password strength based on entropy."""
        if entropy >= 100:
            return "very_strong"
        elif entropy >= 80:
            return "strong"
        elif entropy >= 60:
            return "moderate"
        elif entropy >= 40:
            return "weak"
        else:
            return "very_weak"
    
    def generate_multiple(self, count: int = 1, **kwargs) -> list:
        """Generate multiple passwords."""
        if count <= 0 or count > 100:
            raise ValueError("Count must be between 1 and 100")
            
        return [self.generate_password(**kwargs) for _ in range(count)]