"""Tests for UUIDGenerator class.

This module contains comprehensive tests for the UUIDGenerator class,
testing UUID generation, validation, and various edge cases.
"""

import pytest
import uuid
import re
from src.core.generators.uuid_generator import UUIDGenerator


class TestUUIDGenerator:
    
    def setup_method(self):
        """Setup for each test method."""
        self.generator = UUIDGenerator()
    
    def test_generate_uuid_default(self):
        """Test default UUID generation (v4)."""
        result = self.generator.generate_uuid()
        
        assert "uuid" in result
        assert "version" in result
        assert "type" in result
        assert "description" in result
        assert "format" in result
        assert "length" in result
        assert "timestamp" in result
        assert "components" in result
        assert "metadata" in result
        
        assert result["version"] == "V4"
        assert result["type"] == "Random UUID"
        assert result["description"] == "Cryptographically random UUID"
        assert result["format"] == "8-4-4-4-12 hexadecimal digits"
        assert result["length"] == 36
        
        # Validate UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, result["uuid"])
        
        # Verify it's a valid UUID
        parsed_uuid = uuid.UUID(result["uuid"])
        assert parsed_uuid.version == 4
    
    def test_generate_uuid_v4_explicit(self):
        """Test explicit v4 UUID generation."""
        result = self.generator.generate_uuid("v4")
        
        assert result["version"] == "V4"
        assert result["type"] == "Random UUID"
        
        # Verify it's a valid v4 UUID
        parsed_uuid = uuid.UUID(result["uuid"])
        assert parsed_uuid.version == 4
    
    def test_generate_uuid_v1(self):
        """Test v1 UUID generation."""
        result = self.generator.generate_uuid("v1")
        
        assert result["version"] == "V1"
        assert result["type"] == "Time-based UUID"
        assert result["description"] == "Based on timestamp and MAC address"
        
        # Verify it's a valid v1 UUID
        parsed_uuid = uuid.UUID(result["uuid"])
        assert parsed_uuid.version == 1
    
    def test_generate_uuid_version_formats(self):
        """Test different version format inputs."""
        # Test various ways to specify v4
        for version_input in ['4', 'v4', 'V4']:
            result = self.generator.generate_uuid(version_input)
            assert result["version"] == "V4"
            parsed_uuid = uuid.UUID(result["uuid"])
            assert parsed_uuid.version == 4
        
        # Test various ways to specify v1
        for version_input in ['1', 'v1', 'V1']:
            result = self.generator.generate_uuid(version_input)
            assert result["version"] == "V1"
            parsed_uuid = uuid.UUID(result["uuid"])
            assert parsed_uuid.version == 1
    
    def test_generate_uuid_invalid_version(self):
        """Test UUID generation with invalid version."""
        with pytest.raises(ValueError, match="Unsupported UUID version"):
            self.generator.generate_uuid("v2")
        
        with pytest.raises(ValueError, match="Unsupported UUID version"):
            self.generator.generate_uuid("invalid")
        
        with pytest.raises(ValueError, match="Unsupported UUID version"):
            self.generator.generate_uuid("5")
    
    def test_generate_uuid_components(self):
        """Test UUID components parsing."""
        result = self.generator.generate_uuid("v4")
        components = result["components"]
        
        assert "time_low" in components
        assert "time_mid" in components
        assert "time_hi_and_version" in components
        assert "clock_seq_hi_and_reserved" in components
        assert "clock_seq_low" in components
        assert "node" in components
        
        # Verify component format (hex strings)
        assert re.match(r'^[0-9a-f]+$', components["time_low"])
        assert re.match(r'^[0-9a-f]+$', components["time_mid"])
        assert re.match(r'^[0-9a-f]+$', components["time_hi_and_version"])
        assert re.match(r'^[0-9a-f]+$', components["clock_seq_hi_and_reserved"])
        assert re.match(r'^[0-9a-f]+$', components["clock_seq_low"])
        assert re.match(r'^[0-9a-f]+$', components["node"])
    
    def test_generate_uuid_metadata(self):
        """Test UUID metadata."""
        result = self.generator.generate_uuid("v4")
        metadata = result["metadata"]
        
        assert "variant" in metadata
        assert "is_nil" in metadata
        assert "hex" in metadata
        assert "bytes" in metadata
        
        assert metadata["variant"] == "RFC 4122 variant"
        assert metadata["is_nil"] is False
        assert metadata["bytes"] == 16
        assert len(metadata["hex"]) == 32  # 32 hex chars without dashes
    
    def test_generate_multiple_uuids_default(self):
        """Test multiple UUID generation with default parameters."""
        result = self.generator.generate_multiple_uuids(count=5)

        assert "uuids" in result
        assert "count" in result
        assert "version" in result
        assert "type" in result
        assert "generated_at" in result
        assert "format" in result

        assert result["count"] == 5
        assert result["version"] == "V4"
        assert result["type"] == "Random UUID"
        assert len(result["uuids"]) == 5

        # Verify all UUIDs are unique
        uuid_strings = [u["uuid"] for u in result["uuids"]]
        assert len(set(uuid_strings)) == 5

        # Verify all are valid v4 UUIDs
        for uuid_info in result["uuids"]:
            parsed_uuid = uuid.UUID(uuid_info["uuid"])
            assert parsed_uuid.version == 4

    def test_generate_multiple_uuids_v1(self):
        """Test multiple v1 UUID generation."""
        result = self.generator.generate_multiple_uuids("v1", 3)

        assert result["count"] == 3
        assert result["version"] == "V1"
        assert result["type"] == "Time-based UUID"
        assert len(result["uuids"]) == 3

        # Verify all are valid v1 UUIDs
        for uuid_info in result["uuids"]:
            parsed_uuid = uuid.UUID(uuid_info["uuid"])
            assert parsed_uuid.version == 1

    def test_generate_multiple_uuids_invalid_count(self):
        """Test multiple UUID generation with invalid count."""
        with pytest.raises(ValueError, match="Count must be an integer between 1 and 100"):
            self.generator.generate_multiple_uuids("v4", 0)

        with pytest.raises(ValueError, match="Count must be an integer between 1 and 100"):
            self.generator.generate_multiple_uuids("v4", 101)

        with pytest.raises(ValueError, match="Count must be an integer between 1 and 100"):
            self.generator.generate_multiple_uuids("v4", -1)
    
    def test_validate_uuid_valid(self):
        """Test UUID validation with valid UUIDs."""
        # Generate a valid UUID first
        generated = self.generator.generate_uuid("v4")
        valid_uuid = generated["uuid"]
        
        result = self.generator.validate_uuid(valid_uuid)
        
        assert "is_valid" in result
        assert "uuid" in result
        assert "version" in result
        assert "variant" in result
        assert "type" in result
        assert "description" in result
        assert "components" in result
        assert "metadata" in result
        
        assert result["is_valid"] is True
        assert result["uuid"] == valid_uuid
        assert result["version"] == "V4"
        assert result["variant"] == "RFC 4122 variant"
    
    def test_validate_uuid_invalid_format(self):
        """Test UUID validation with invalid format."""
        invalid_uuids = [
            "invalid-uuid",
            "123e4567-e89b-12d3-a456-42661440000",  # Too short
            "123e4567-e89b-12d3-a456-4266144000000",  # Too long
            "123e4567-e89b-12d3-a456-42661440000g",  # Invalid character
            "123e4567e89b12d3a45642661440000",  # Missing dashes
            "",  # Empty string
            "123e4567-e89b-12d3-a456",  # Incomplete
        ]
        
        for invalid_uuid in invalid_uuids:
            result = self.generator.validate_uuid(invalid_uuid)
            
            assert result["is_valid"] is False
            assert "error" in result
            assert "suggestions" in result
            assert result["input"] == invalid_uuid
    
    def test_validate_uuid_non_string_input(self):
        """Test UUID validation with non-string input."""
        with pytest.raises(ValueError, match="UUID must be a string"):
            self.generator.validate_uuid(123)
        
        with pytest.raises(ValueError, match="UUID must be a string"):
            self.generator.validate_uuid(None)
        
        with pytest.raises(ValueError, match="UUID must be a string"):
            self.generator.validate_uuid([])
    
    def test_validate_uuid_whitespace_handling(self):
        """Test UUID validation handles whitespace."""
        # Generate a valid UUID and add whitespace
        generated = self.generator.generate_uuid("v4")
        valid_uuid = generated["uuid"]
        uuid_with_whitespace = f"  {valid_uuid}  "
        
        result = self.generator.validate_uuid(uuid_with_whitespace)
        
        assert result["is_valid"] is True
        assert result["uuid"] == valid_uuid  # Should be trimmed
    
    def test_validate_uuid_nil_uuid(self):
        """Test validation of nil UUID."""
        nil_uuid = "00000000-0000-0000-0000-000000000000"
        result = self.generator.validate_uuid(nil_uuid)
        
        assert result["is_valid"] is True
        assert result["uuid"] == nil_uuid
        assert result["metadata"]["is_nil"] is True
    
    def test_uuid_uniqueness(self):
        """Test that generated UUIDs are unique."""
        uuids = []
        for _ in range(100):
            result = self.generator.generate_uuid("v4")
            uuids.append(result["uuid"])
        
        # All UUIDs should be unique
        assert len(set(uuids)) == 100
    
    def test_uuid_format_consistency(self):
        """Test that all generated UUIDs follow the same format."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        for _ in range(10):
            result = self.generator.generate_uuid("v4")
            assert re.match(uuid_pattern, result["uuid"])
            assert result["length"] == 36
            assert result["format"] == "8-4-4-4-12 hexadecimal digits"
    
    def test_supported_versions(self):
        """Test that supported versions are accessible."""
        supported = self.generator.SUPPORTED_VERSIONS

        assert '1' in supported
        assert '4' in supported
        assert 'v1' in supported
        assert 'v4' in supported
        assert len(supported) == 4
    
    def test_version_description_method(self):
        """Test _get_version_description method indirectly."""
        v1_result = self.generator.generate_uuid("v1")
        v4_result = self.generator.generate_uuid("v4")
        
        assert v1_result["type"] == "Time-based UUID"
        assert v1_result["description"] == "Based on timestamp and MAC address"
        
        assert v4_result["type"] == "Random UUID"
        assert v4_result["description"] == "Cryptographically random UUID"
    
    def test_uuid_variant_detection(self):
        """Test UUID variant detection."""
        result = self.generator.generate_uuid("v4")
        
        # Modern UUIDs should be RFC 4122 variant
        assert result["metadata"]["variant"] == "RFC 4122 variant"
        
        # Verify the actual UUID object has correct variant
        parsed_uuid = uuid.UUID(result["uuid"])
        assert parsed_uuid.variant == uuid.RFC_4122
