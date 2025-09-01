"""URL Utility for encoding and decoding operations.

This module provides functionality to encode and decode URLs
with proper validation and different encoding types.
"""

import urllib.parse
from typing import Dict, Any


class URLUtility:
    """Utility for URL encoding and decoding operations."""
    
    def __init__(self):
        """Initialize the URL Utility."""
        pass
    
    def encode(self, text: str, encoding_type: str = 'standard') -> Dict[str, Any]:
        """
        Encode text for URL usage.
        
        Args:
            text (str): Text to encode
            encoding_type (str): Type of encoding ('standard', 'plus', 'component')
            
        Returns:
            Dict containing encoded result and metadata
            
        Raises:
            ValueError: If input is invalid
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        if not text:
            raise ValueError("Input text cannot be empty")
        
        encoding_type = encoding_type.lower().strip()
        
        if encoding_type not in ['standard', 'plus', 'component']:
            raise ValueError("Encoding type must be one of: 'standard', 'plus', 'component'")
        
        try:
            if encoding_type == 'standard':
                # Standard URL encoding (percent encoding)
                encoded = urllib.parse.quote(text)
                description = "Standard percent encoding (RFC 3986)"
                
            elif encoding_type == 'plus':
                # URL encoding with + for spaces (application/x-www-form-urlencoded)
                encoded = urllib.parse.quote_plus(text)
                description = "Form data encoding (+ for spaces)"
                
            else:  # component
                # Component encoding (more aggressive)
                encoded = urllib.parse.quote(text, safe='')
                description = "Component encoding (encode all special characters)"
            
            # Calculate encoding statistics
            original_length = len(text)
            encoded_length = len(encoded)
            percent_chars = encoded.count('%')
            plus_chars = encoded.count('+') if encoding_type == 'plus' else 0
            
            size_increase = ((encoded_length - original_length) / original_length) * 100 if original_length > 0 else 0
            
            return {
                "encoded": encoded,
                "original_text": text,
                "encoding_type": encoding_type,
                "description": description,
                "original_length": original_length,
                "encoded_length": encoded_length,
                "size_increase_percent": round(size_increase, 2),
                "percent_encoded_chars": percent_chars,
                "plus_encoded_chars": plus_chars,
                "characters_encoded": percent_chars + plus_chars,
                "safe_characters": self._get_safe_characters(encoding_type)
            }
            
        except Exception as e:
            raise ValueError(f"Error encoding URL: {str(e)}")
    
    def decode(self, encoded_text: str, encoding_type: str = 'standard') -> Dict[str, Any]:
        """
        Decode URL-encoded text.
        
        Args:
            encoded_text (str): URL-encoded text to decode
            encoding_type (str): Type of decoding to use
            
        Returns:
            Dict containing decoded result and metadata
            
        Raises:
            ValueError: If input is invalid
        """
        if not isinstance(encoded_text, str):
            raise ValueError("Input must be a string")
        
        if not encoded_text:
            raise ValueError("Input text cannot be empty")
        
        encoding_type = encoding_type.lower().strip()
        
        if encoding_type not in ['standard', 'plus', 'auto']:
            raise ValueError("Decoding type must be one of: 'standard', 'plus', 'auto'")
        
        try:
            if encoding_type == 'auto':
                # Auto-detect based on content
                if '+' in encoded_text and '%20' not in encoded_text:
                    decoded = urllib.parse.unquote_plus(encoded_text)
                    detected_type = 'plus'
                    description = "Auto-detected: Form data encoding (+ for spaces)"
                else:
                    decoded = urllib.parse.unquote(encoded_text)
                    detected_type = 'standard'
                    description = "Auto-detected: Standard percent encoding"
            elif encoding_type == 'plus':
                decoded = urllib.parse.unquote_plus(encoded_text)
                detected_type = 'plus'
                description = "Form data decoding (+ to spaces)"
            else:  # standard
                decoded = urllib.parse.unquote(encoded_text)
                detected_type = 'standard'
                description = "Standard percent decoding"
            
            # Calculate decoding statistics
            encoded_length = len(encoded_text)
            decoded_length = len(decoded)
            percent_chars = encoded_text.count('%')
            plus_chars = encoded_text.count('+')
            
            size_decrease = ((encoded_length - decoded_length) / encoded_length) * 100 if encoded_length > 0 else 0
            
            return {
                "decoded": decoded,
                "original_encoded": encoded_text,
                "decoding_type": detected_type if encoding_type == 'auto' else encoding_type,
                "description": description,
                "encoded_length": encoded_length,
                "decoded_length": decoded_length,
                "size_decrease_percent": round(size_decrease, 2),
                "percent_encoded_chars": percent_chars,
                "plus_encoded_chars": plus_chars,
                "characters_decoded": percent_chars + (plus_chars if detected_type == 'plus' else 0)
            }
            
        except Exception as e:
            raise ValueError(f"Error decoding URL: {str(e)}")
    
    def validate(self, text: str) -> Dict[str, Any]:
        """
        Validate if text is properly URL-encoded.
        
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
        
        if not text:
            return {
                "is_valid": False,
                "error": "Input cannot be empty",
                "suggestions": ["Provide non-empty URL-encoded string"]
            }
        
        validation_results = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "statistics": {
                "percent_sequences": text.count('%'),
                "plus_signs": text.count('+'),
                "length": len(text)
            }
        }
        
        # Check for malformed percent encoding
        percent_positions = []
        i = 0
        while i < len(text):
            if text[i] == '%':
                percent_positions.append(i)
                if i + 2 >= len(text):
                    validation_results["is_valid"] = False
                    validation_results["issues"].append(f"Incomplete percent sequence at position {i}")
                else:
                    hex_part = text[i+1:i+3]
                    if not all(c in '0123456789ABCDEFabcdef' for c in hex_part):
                        validation_results["is_valid"] = False
                        validation_results["issues"].append(f"Invalid hex characters in percent sequence at position {i}: %{hex_part}")
                i += 3
            else:
                i += 1
        
        # Check for unsafe characters that should be encoded
        unsafe_chars = set(' "<>%{}|\\^`[]')
        found_unsafe = []
        for i, char in enumerate(text):
            if char in unsafe_chars and char != '%':  # % is OK if part of encoding
                found_unsafe.append((char, i))
        
        if found_unsafe:
            validation_results["warnings"].append(f"Found {len(found_unsafe)} potentially unsafe unencoded characters")
        
        # Try to decode to check if it's decodable
        try:
            decoded = urllib.parse.unquote(text)
            can_decode = True
            decode_error = None
        except Exception as e:
            can_decode = False
            decode_error = str(e)
            validation_results["is_valid"] = False
            validation_results["issues"].append(f"Cannot decode: {decode_error}")
        
        validation_results.update({
            "can_decode": can_decode,
            "decode_error": decode_error,
            "unsafe_characters": [{"char": char, "position": pos} for char, pos in found_unsafe],
            "encoding_detection": self._detect_encoding_type(text)
        })
        
        if validation_results["is_valid"]:
            validation_results["suggestions"] = [
                "URL encoding appears to be valid",
                "Consider the appropriate decoding method based on context"
            ]
        else:
            validation_results["suggestions"] = [
                "Fix malformed percent sequences",
                "Ensure all % characters are followed by 2 hex digits",
                "Consider encoding unsafe characters"
            ]
        
        return validation_results
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about URL encoding.
        
        Returns:
            Dict containing URL encoding information
        """
        return {
            "name": "URL Encoding (Percent Encoding)",
            "description": "Encoding mechanism to represent characters in URLs that are not allowed or have special meaning",
            "standard": "RFC 3986",
            "encoding_types": {
                "standard": {
                    "description": "Standard percent encoding",
                    "spaces": "Encoded as %20",
                    "use_case": "General URL components"
                },
                "plus": {
                    "description": "Form data encoding",
                    "spaces": "Encoded as +",
                    "use_case": "HTML form data (application/x-www-form-urlencoded)"
                },
                "component": {
                    "description": "Component encoding",
                    "spaces": "Encoded as %20",
                    "use_case": "URL path components (more restrictive)"
                }
            },
            "reserved_characters": {
                "general_delimiters": ": / ? # [ ] @",
                "sub_delimiters": "! $ & ' ( ) * + , ; =",
                "description": "Characters with special meaning in URLs"
            },
            "unsafe_characters": {
                "always_encode": "space \" < > % { } | \\ ^ ` [ ]",
                "description": "Characters that should always be encoded in URLs"
            },
            "percent_encoding": {
                "format": "%XX where XX is hexadecimal representation",
                "example": "Hello World → Hello%20World",
                "case_sensitivity": "Hex digits can be upper or lower case"
            },
            "common_encodings": {
                " ": "%20 or +",
                "!": "%21",
                "\"": "%22",
                "#": "%23",
                "$": "%24",
                "%": "%25",
                "&": "%26",
                "'": "%27",
                "(": "%28",
                ")": "%29",
                "*": "%2A",
                "+": "%2B",
                ",": "%2C",
                "/": "%2F",
                ":": "%3A",
                ";": "%3B",
                "=": "%3D",
                "?": "%3F",
                "@": "%40",
                "[": "%5B",
                "]": "%5D"
            }
        }
    
    def _get_safe_characters(self, encoding_type: str) -> str:
        """Get safe characters for encoding type."""
        if encoding_type == 'standard':
            return "A-Z a-z 0-9 - . _ ~ : / ? # [ ] @ ! $ & ' ( ) * + , ; ="
        elif encoding_type == 'plus':
            return "A-Z a-z 0-9 - . _ ~ : / ? # [ ] @ ! $ & ' ( ) * , ; ="
        else:  # component
            return "A-Z a-z 0-9 - . _ ~"
    
    def _detect_encoding_type(self, text: str) -> Dict[str, Any]:
        """Detect the likely encoding type used."""
        has_percent = '%' in text
        has_plus = '+' in text
        has_space_encoded = '%20' in text
        
        if has_plus and not has_space_encoded:
            likely_type = 'plus'
            confidence = 'high'
        elif has_percent and not has_plus:
            likely_type = 'standard'
            confidence = 'high'
        elif has_percent and has_plus:
            likely_type = 'mixed'
            confidence = 'low'
        else:
            likely_type = 'none'
            confidence = 'high'
        
        return {
            "likely_type": likely_type,
            "confidence": confidence,
            "indicators": {
                "has_percent_encoding": has_percent,
                "has_plus_encoding": has_plus,
                "has_percent20": has_space_encoded
            }
        }