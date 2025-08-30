import secrets
import base64
import string
import math
from typing import Literal


class APIKeyGenerator:
    
    def __init__(self):
        pass
    
    def generate_hex(self, length: int = 32) -> str:
        """Generate hexadecimal API key."""
        if length <= 0 or length > 128:
            raise ValueError("Length must be between 1 and 128 bytes")
        return secrets.token_hex(length)
    
    def generate_base64(self, length: int = 24) -> str:
        """Generate base64 URL-safe API key."""
        if length <= 0 or length > 128:
            raise ValueError("Length must be between 1 and 128 bytes")
        return secrets.token_urlsafe(length)
    
    def generate_base58(self, length: int = 32) -> str:
        """Generate base58 API key (Bitcoin-style encoding)."""
        if length <= 0 or length > 128:
            raise ValueError("Length must be between 1 and 128 bytes")
            
        # Base58 alphabet (no 0, O, I, l to avoid confusion)
        base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        
        # Generate random bytes
        random_bytes = secrets.token_bytes(length)
        
        # Convert to base58
        num = int.from_bytes(random_bytes, 'big')
        encoded = ""
        
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded = base58_alphabet[remainder] + encoded
            
        # Handle leading zeros
        leading_zeros = len(random_bytes) - len(random_bytes.lstrip(b'\x00'))
        encoded = '1' * leading_zeros + encoded
        
        return encoded
    
    def generate_custom(self, 
                       length: int = 32,
                       charset: str = None) -> str:
        """Generate API key with custom character set."""
        
        if charset is None:
            charset = string.ascii_letters + string.digits
            
        if length <= 0 or length > 256:
            raise ValueError("Length must be between 1 and 256 characters")
            
        if len(charset) < 2:
            raise ValueError("Charset must contain at least 2 characters")
            
        return "".join(secrets.choice(charset) for _ in range(length))
    
    def generate(self,
                key_format: Literal["hex", "base64", "base58", "custom"] = "hex",
                length: int = 32,
                prefix: str = "",
                charset: str = None) -> dict:
        """Main API key generation method."""
        
        if prefix and len(prefix) > 20:
            raise ValueError("Prefix cannot exceed 20 characters")
            
        # Generate based on format
        if key_format == "hex":
            key = self.generate_hex(length)
        elif key_format == "base64":
            key = self.generate_base64(length)
        elif key_format == "base58":
            key = self.generate_base58(length)
        elif key_format == "custom":
            key = self.generate_custom(length, charset)
        else:
            raise ValueError(f"Invalid format: {key_format}")
            
        # Add prefix if specified
        final_key = prefix + key if prefix else key
        
        # Calculate entropy (approximate for encoded formats)
        if key_format == "hex":
            entropy_bits = length * 4  # 4 bits per hex char
        elif key_format == "base64":
            entropy_bits = length * 6  # ~6 bits per base64 char
        elif key_format == "base58":
            entropy_bits = length * math.log2(58)  # ~5.86 bits per base58 char
        else:
            entropy_bits = length * math.log2(len(charset or ""))
            
        return {
            "api_key": final_key,
            "format": key_format,
            "length": len(key),
            "total_length": len(final_key),
            "prefix": prefix,
            "entropy_bits": round(entropy_bits, 2),
            "security_level": self._assess_security(entropy_bits)
        }
    
    def _assess_security(self, entropy_bits: float) -> str:
        """Assess API key security level based on entropy."""
        if entropy_bits >= 256:
            return "military_grade"
        elif entropy_bits >= 128:
            return "very_strong"
        elif entropy_bits >= 80:
            return "strong"
        elif entropy_bits >= 64:
            return "adequate"
        else:
            return "weak"
    
    def generate_multiple(self, count: int = 1, **kwargs) -> list:
        """Generate multiple API keys."""
        if count <= 0 or count > 50:
            raise ValueError("Count must be between 1 and 50")
            
        return [self.generate(**kwargs) for _ in range(count)]