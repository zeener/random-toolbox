"""Base64 Utility for encoding and decoding operations.

This module provides functionality to encode and decode Base64 strings
with proper validation and error handling.
"""

import base64
import binascii
from typing import Dict, Any


class Base64Utility:
    """Utility for Base64 encoding and decoding operations."""
    
    def __init__(self):
        """Initialize the Base64 Utility."""
        pass
    
    def encode(self, text: str) -> Dict[str, Any]:
        """
        Encode text to Base64.
        
        Args:
            text (str): Text to encode
            
        Returns:
            Dict containing encoded result and metadata
            
        Raises:
            ValueError: If input is invalid
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        if not text:
            raise ValueError("Input text cannot be empty")
        
        try:
            # Encode string to bytes using UTF-8, then to Base64
            text_bytes = text.encode('utf-8')
            encoded_bytes = base64.b64encode(text_bytes)
            encoded_string = encoded_bytes.decode('ascii')
            
            # Calculate size increase
            original_size = len(text)
            encoded_size = len(encoded_string)
            size_increase = ((encoded_size - original_size) / original_size) * 100 if original_size > 0 else 0
            
            return {
                "encoded": encoded_string,
                "original_text": text,
                "original_length": original_size,
                "encoded_length": encoded_size,
                "size_increase_percent": round(size_increase, 2),
                "encoding": "utf-8",
                "padding_chars": encoded_string.count('='),
                "is_valid_base64": self._is_valid_base64(encoded_string)
            }
            
        except Exception as e:
            raise ValueError(f"Error encoding to Base64: {str(e)}")
    
    def decode(self, encoded_text: str) -> Dict[str, Any]:
        """
        Decode Base64 text to original string.
        
        Args:
            encoded_text (str): Base64 encoded text to decode
            
        Returns:
            Dict containing decoded result and metadata
            
        Raises:
            ValueError: If input is invalid or not proper Base64
        """
        if not isinstance(encoded_text, str):
            raise ValueError("Input must be a string")
        
        if not encoded_text:
            raise ValueError("Input text cannot be empty")
        
        # Clean input - remove whitespace
        encoded_text = encoded_text.strip()
        
        # Validate Base64 format
        if not self._is_valid_base64(encoded_text):
            raise ValueError("Invalid Base64 format. Base64 should contain only A-Z, a-z, 0-9, +, /, and = for padding")
        
        try:
            # Decode Base64 to bytes, then to UTF-8 string
            decoded_bytes = base64.b64decode(encoded_text)
            decoded_string = decoded_bytes.decode('utf-8')
            
            # Calculate size decrease
            encoded_size = len(encoded_text)
            decoded_size = len(decoded_string)
            size_decrease = ((encoded_size - decoded_size) / encoded_size) * 100 if encoded_size > 0 else 0
            
            return {
                "decoded": decoded_string,
                "original_encoded": encoded_text,
                "encoded_length": encoded_size,
                "decoded_length": decoded_size,
                "size_decrease_percent": round(size_decrease, 2),
                "encoding": "utf-8",
                "padding_chars": encoded_text.count('='),
                "bytes_decoded": len(decoded_bytes)
            }
            
        except base64.binascii.Error as e:
            raise ValueError(f"Invalid Base64 input: {str(e)}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Decoded bytes are not valid UTF-8 text: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error decoding Base64: {str(e)}")
    
    def validate(self, text: str) -> Dict[str, Any]:
        """
        Validate if text is proper Base64 format.
        
        Args:
            text (str): Text to validate
            
        Returns:
            Dict containing validation results
        """
        if not isinstance(text, str):
            return {
                "is_valid": False,
                "error": "Input must be a string",
                "suggestions": ["Provide a string input"]
            }
        
        text = text.strip()
        
        if not text:
            return {
                "is_valid": False,
                "error": "Input cannot be empty",
                "suggestions": ["Provide non-empty Base64 string"]
            }
        
        is_valid = self._is_valid_base64(text)
        
        if is_valid:
            try:
                # Try to decode to check if it's decodable
                base64.b64decode(text, validate=True)
                can_decode = True
                decode_error = None
            except Exception as e:
                can_decode = False
                decode_error = str(e)
            
            return {
                "is_valid": True,
                "can_decode": can_decode,
                "decode_error": decode_error,
                "length": len(text),
                "padding_chars": text.count('='),
                "format_info": {
                    "alphabet": "A-Z, a-z, 0-9, +, /",
                    "padding": "= characters",
                    "line_breaks": "Optional (ignored during decoding)"
                }
            }
        else:
            return {
                "is_valid": False,
                "error": "Invalid Base64 format",
                "suggestions": [
                    "Base64 should contain only A-Z, a-z, 0-9, +, / characters",
                    "Padding with = characters should only be at the end",
                    "Length should be multiple of 4 (after padding)",
                    "Example: SGVsbG8gV29ybGQ="
                ],
                "common_issues": [
                    "Invalid characters in string",
                    "Incorrect padding",
                    "Wrong length (not multiple of 4)"
                ]
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about Base64 encoding.
        
        Returns:
            Dict containing Base64 information
        """
        return {
            "name": "Base64 Encoding",
            "description": "Binary-to-text encoding scheme that represents binary data in ASCII string format",
            "alphabet": "A-Z, a-z, 0-9, +, /",
            "padding_character": "=",
            "encoding_ratio": "4:3 (4 Base64 characters represent 3 bytes of data)",
            "size_increase": "~33% increase from original size",
            "use_cases": [
                "Email attachments (MIME)",
                "Data URLs in web development",
                "Storing binary data in text format",
                "API data transmission",
                "Configuration files"
            ],
            "variants": {
                "standard": "Uses +, / with = padding",
                "url_safe": "Uses -, _ instead of +, / (RFC 4648)",
                "no_padding": "Omits = padding characters"
            },
            "characteristics": [
                "Reversible encoding",
                "Case sensitive",
                "Safe for text-based protocols",
                "No line length restrictions in modern usage"
            ]
        }
    
    def _is_valid_base64(self, text: str) -> bool:
        """
        Check if string is valid Base64 format.
        
        Args:
            text (str): Text to validate
            
        Returns:
            bool: True if valid Base64 format
        """
        try:
            # Remove whitespace
            text = ''.join(text.split())
            
            # Check length (must be multiple of 4)
            if len(text) % 4 != 0:
                return False
            
            # Check alphabet and padding
            base64_alphabet = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
            
            if not all(c in base64_alphabet for c in text):
                return False
            
            # Check padding (= can only be at the end)
            if '=' in text:
                padding_start = text.find('=')
                if not text[padding_start:].replace('=', ''):
                    # All characters after first = must be =
                    if text[padding_start:] in ['=', '==']:
                        return True
                    else:
                        return False
                else:
                    return False
            
            return True
            
        except Exception:
            return False