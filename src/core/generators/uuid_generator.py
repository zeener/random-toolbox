"""UUID Generator for generating unique identifiers.

This module provides functionality to generate UUIDs in various versions
(UUID1, UUID4) with proper validation and metadata.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime


class UUIDGenerator:
    """Generator for creating UUID values in different versions."""
    
    SUPPORTED_VERSIONS = ['1', '4', 'v1', 'v4']
    
    def __init__(self):
        """Initialize the UUID Generator."""
        pass
    
    def generate_uuid(self, version: str = 'v4') -> Dict[str, Any]:
        """
        Generate UUID of specified version.
        
        Args:
            version (str): UUID version ('1', '4', 'v1', 'v4')
            
        Returns:
            Dict containing UUID and metadata
            
        Raises:
            ValueError: If version is not supported
        """
        version = str(version).lower().strip()
        
        # Normalize version format
        if version in ['1', 'v1']:
            version = 'v1'
        elif version in ['4', 'v4']:
            version = 'v4'
        else:
            raise ValueError(f"Unsupported UUID version: {version}. "
                           f"Supported versions: {', '.join(self.SUPPORTED_VERSIONS)}")
        
        try:
            if version == 'v1':
                generated_uuid = uuid.uuid1()
                uuid_type = "Time-based UUID"
                description = "Based on timestamp and MAC address"
            else:  # v4
                generated_uuid = uuid.uuid4()
                uuid_type = "Random UUID"
                description = "Cryptographically random UUID"
            
            uuid_string = str(generated_uuid)
            
            return {
                "uuid": uuid_string,
                "version": version.upper(),
                "type": uuid_type,
                "description": description,
                "format": "8-4-4-4-12 hexadecimal digits",
                "length": len(uuid_string),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "components": self._parse_uuid_components(generated_uuid),
                "metadata": {
                    "variant": self._get_uuid_variant(generated_uuid),
                    "is_nil": generated_uuid.int == 0,
                    "hex": generated_uuid.hex,
                    "bytes": len(generated_uuid.bytes),
                    "fields": {
                        "time_low": generated_uuid.time_low if version == 'v1' else None,
                        "time_mid": generated_uuid.time_mid if version == 'v1' else None,
                        "time_hi_version": generated_uuid.time_hi_version if version == 'v1' else None,
                        "clock_seq_hi_variant": generated_uuid.clock_seq_hi_variant if version == 'v1' else None,
                        "clock_seq_low": generated_uuid.clock_seq_low if version == 'v1' else None,
                        "node": generated_uuid.node if version == 'v1' else None,
                    }
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error generating UUID: {str(e)}")
    
    def generate_multiple_uuids(self, version: str = 'v4', count: int = 5) -> Dict[str, Any]:
        """
        Generate multiple UUIDs of the same version.
        
        Args:
            version (str): UUID version to generate
            count (int): Number of UUIDs to generate (1-100)
            
        Returns:
            Dict containing list of UUIDs and metadata
        """
        if not isinstance(count, int) or count < 1 or count > 100:
            raise ValueError("Count must be an integer between 1 and 100")
        
        uuids = []
        
        for _ in range(count):
            result = self.generate_uuid(version)
            uuids.append({
                "uuid": result["uuid"],
                "timestamp": result["timestamp"],
                "hex": result["metadata"]["hex"]
            })
        
        return {
            "uuids": uuids,
            "count": count,
            "version": version.upper(),
            "type": self._get_version_description(version)["type"],
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "format": "8-4-4-4-12 hexadecimal digits"
        }
    
    def validate_uuid(self, uuid_string: str) -> Dict[str, Any]:
        """
        Validate and analyze a UUID string.
        
        Args:
            uuid_string (str): UUID string to validate
            
        Returns:
            Dict containing validation results and analysis
        """
        if not isinstance(uuid_string, str):
            raise ValueError("UUID must be a string")
        
        uuid_string = uuid_string.strip()
        
        try:
            parsed_uuid = uuid.UUID(uuid_string)
            is_valid = True
            error = None
            
        except ValueError as e:
            is_valid = False
            error = str(e)
            parsed_uuid = None
        
        if is_valid:
            version = f"v{parsed_uuid.version}"
            version_info = self._get_version_description(version)
            
            return {
                "is_valid": True,
                "uuid": str(parsed_uuid),
                "version": version.upper(),
                "type": version_info["type"],
                "description": version_info["description"],
                "variant": self._get_uuid_variant(parsed_uuid),
                "format": "8-4-4-4-12 hexadecimal digits",
                "length": len(str(parsed_uuid)),
                "components": self._parse_uuid_components(parsed_uuid),
                "metadata": {
                    "is_nil": parsed_uuid.int == 0,
                    "hex": parsed_uuid.hex,
                    "bytes_length": len(parsed_uuid.bytes)
                }
            }
        else:
            return {
                "is_valid": False,
                "error": error,
                "input": uuid_string,
                "suggestions": [
                    "UUID should be in format: 8-4-4-4-12 hexadecimal digits",
                    "Example: 550e8400-e29b-41d4-a716-446655440000",
                    "Check for correct length (36 characters with dashes)"
                ]
            }
    
    def get_supported_versions(self) -> Dict[str, Any]:
        """
        Get information about supported UUID versions.
        
        Returns:
            Dict containing version information
        """
        return {
            "versions": {
                "v1": {
                    "name": "Time-based UUID",
                    "description": "Based on timestamp and MAC address",
                    "use_case": "When you need UUIDs that can be sorted by creation time",
                    "privacy": "Contains MAC address (privacy concern)",
                    "uniqueness": "Guaranteed unique across space and time"
                },
                "v4": {
                    "name": "Random UUID",
                    "description": "Cryptographically random UUID",
                    "use_case": "General purpose, most commonly used",
                    "privacy": "No personally identifiable information",
                    "uniqueness": "Statistically unique (extremely low collision probability)"
                }
            },
            "format": "8-4-4-4-12 hexadecimal digits separated by hyphens",
            "total_length": 36,
            "example": "550e8400-e29b-41d4-a716-446655440000"
        }
    
    def _parse_uuid_components(self, uuid_obj: uuid.UUID) -> Dict[str, str]:
        """Parse UUID into its component parts."""
        uuid_string = str(uuid_obj)
        parts = uuid_string.split('-')
        
        return {
            "time_low": parts[0],
            "time_mid": parts[1], 
            "time_hi_and_version": parts[2],
            "clock_seq_hi_and_reserved": parts[3][:2],
            "clock_seq_low": parts[3][2:],
            "node": parts[4]
        }
    
    def _get_uuid_variant(self, uuid_obj: uuid.UUID) -> str:
        """Get UUID variant information."""
        variant = uuid_obj.variant
        
        variant_map = {
            uuid.RESERVED_NCS: "Reserved for NCS compatibility",
            uuid.RFC_4122: "RFC 4122 variant",
            uuid.RESERVED_MICROSOFT: "Reserved for Microsoft compatibility",
            uuid.RESERVED_FUTURE: "Reserved for future definition"
        }
        
        return variant_map.get(variant, f"Unknown variant ({variant})")
    
    def _get_version_description(self, version: str) -> Dict[str, str]:
        """Get description for UUID version."""
        version = version.lower()
        
        descriptions = {
            'v1': {
                "type": "Time-based UUID",
                "description": "Based on timestamp and MAC address"
            },
            'v4': {
                "type": "Random UUID", 
                "description": "Cryptographically random UUID"
            }
        }
        
        return descriptions.get(version, {
            "type": "Unknown",
            "description": "Unknown UUID version"
        })