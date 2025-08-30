import pytest
import sys
import os
import re
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.cli.main import cli


class TestCLI:
    
    def setup_method(self):
        """Setup for each test method."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test main CLI help command."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Random Toolbox" in result.output
        assert "text" in result.output
        assert "password" in result.output
        assert "apikey" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    # Text Command Tests
    def test_text_command_default(self):
        """Test text command with default parameters."""
        result = self.runner.invoke(cli, ['text'])
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0
    
    def test_text_command_words(self):
        """Test text command with word generation."""
        result = self.runner.invoke(cli, ['text', '--type', 'word', '--count', '3'])
        assert result.exit_code == 0
        
        words = result.output.strip().split('\n')
        assert len(words) == 3
        assert all(len(word.strip()) > 0 for word in words)
    
    def test_text_command_sentences(self):
        """Test text command with sentence generation."""
        result = self.runner.invoke(cli, ['text', '--type', 'sentence', '--count', '2'])
        assert result.exit_code == 0
        
        sentences = result.output.strip().split('\n')
        assert len(sentences) == 2
        assert all(sentence.strip().endswith('.') for sentence in sentences)
    
    def test_text_command_paragraphs(self):
        """Test text command with paragraph generation."""
        result = self.runner.invoke(cli, ['text', '--type', 'paragraph', '--count', '2'])
        assert result.exit_code == 0
        
        paragraphs = result.output.strip().split('\n')
        assert len(paragraphs) == 2
        assert all('.' in paragraph for paragraph in paragraphs)
    
    def test_text_command_invalid_type(self):
        """Test text command with invalid type."""
        result = self.runner.invoke(cli, ['text', '--type', 'invalid'])
        assert result.exit_code == 2  # Click argument error
    
    def test_text_command_help(self):
        """Test text command help."""
        result = self.runner.invoke(cli, ['text', '--help'])
        assert result.exit_code == 0
        assert "Generate random text" in result.output
        assert "--type" in result.output
        assert "--count" in result.output
    
    # Password Command Tests
    def test_password_command_default(self):
        """Test password command with default parameters."""
        result = self.runner.invoke(cli, ['password'])
        assert result.exit_code == 0
        
        password = result.output.strip()
        assert len(password) == 16
        assert isinstance(password, str)
    
    def test_password_command_custom_length(self):
        """Test password command with custom length."""
        result = self.runner.invoke(cli, ['password', '--length', '12'])
        assert result.exit_code == 0
        
        password = result.output.strip()
        assert len(password) == 12
    
    def test_password_command_with_symbols(self):
        """Test password command with symbols enabled."""
        result = self.runner.invoke(cli, ['password', '--length', '20', '--symbols'])
        assert result.exit_code == 0
        
        password = result.output.strip()
        assert len(password) == 20
        
        # Should contain at least one symbol
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        assert any(c in symbols for c in password)
    
    def test_password_command_show_entropy(self):
        """Test password command with entropy display."""
        result = self.runner.invoke(cli, ['password', '--show-entropy'])
        assert result.exit_code == 0
        
        lines = result.output.strip().split('\n')
        assert len(lines) >= 4  # Password + 3 info lines
        
        # Check that entropy info is in stderr output
        assert any("Length:" in line for line in lines)
        assert any("Entropy:" in line for line in lines)
        assert any("Strength:" in line for line in lines)
    
    def test_password_command_invalid_length(self):
        """Test password command with invalid length."""
        result = self.runner.invoke(cli, ['password', '--length', '5'])
        assert result.exit_code == 1
        assert "Error:" in result.output
    
    def test_password_command_exclude_ambiguous(self):
        """Test password command with ambiguous character exclusion."""
        result = self.runner.invoke(cli, ['password', '--length', '50', '--exclude-ambiguous'])
        assert result.exit_code == 0
        
        password = result.output.strip()
        ambiguous = "0O1lI|`'"
        assert not any(c in ambiguous for c in password)
    
    def test_password_command_help(self):
        """Test password command help."""
        result = self.runner.invoke(cli, ['password', '--help'])
        assert result.exit_code == 0
        assert "Generate secure random passwords" in result.output
        assert "--length" in result.output
        assert "--symbols" in result.output
    
    # API Key Command Tests
    def test_apikey_command_default(self):
        """Test apikey command with default parameters."""
        result = self.runner.invoke(cli, ['apikey'])
        assert result.exit_code == 0
        
        key = result.output.strip()
        assert len(key) == 64  # 32 bytes = 64 hex chars
        assert re.match(r'^[0-9a-f]+$', key)
    
    def test_apikey_command_base64(self):
        """Test apikey command with base64 format."""
        result = self.runner.invoke(cli, ['apikey', '--format', 'base64'])
        assert result.exit_code == 0
        
        key = result.output.strip()
        assert re.match(r'^[A-Za-z0-9_-]+$', key)
    
    def test_apikey_command_with_prefix(self):
        """Test apikey command with prefix."""
        result = self.runner.invoke(cli, ['apikey', '--prefix', 'sk_'])
        assert result.exit_code == 0
        
        key = result.output.strip()
        assert key.startswith('sk_')
    
    def test_apikey_command_show_entropy(self):
        """Test apikey command with entropy display."""
        result = self.runner.invoke(cli, ['apikey', '--show-entropy'])
        assert result.exit_code == 0
        
        lines = result.output.strip().split('\n')
        assert len(lines) >= 5  # Key + 4 info lines
        
        assert any("Format:" in line for line in lines)
        assert any("Length:" in line for line in lines)
        assert any("Entropy:" in line for line in lines)
        assert any("Security:" in line for line in lines)
    
    def test_apikey_command_custom_format(self):
        """Test apikey command with custom format."""
        result = self.runner.invoke(cli, ['apikey', '--format', 'custom', '--charset', 'ABC123'])
        assert result.exit_code == 0
        
        key = result.output.strip()
        assert all(c in 'ABC123' for c in key)
    
    def test_apikey_command_help(self):
        """Test apikey command help."""
        result = self.runner.invoke(cli, ['apikey', '--help'])
        assert result.exit_code == 0
        assert "Generate secure API keys" in result.output
        assert "--format" in result.output
        assert "--prefix" in result.output
    
    # Integration Tests
    def test_multiple_commands_work(self):
        """Test that multiple commands can be run in sequence."""
        # Run text command
        result1 = self.runner.invoke(cli, ['text', '--type', 'word', '--count', '1'])
        assert result1.exit_code == 0
        
        # Run password command
        result2 = self.runner.invoke(cli, ['password', '--length', '8'])
        assert result2.exit_code == 0
        
        # Run apikey command
        result3 = self.runner.invoke(cli, ['apikey', '--length', '16'])
        assert result3.exit_code == 0
        
        # All should produce different outputs
        outputs = [result1.output.strip(), result2.output.strip(), result3.output.strip()]
        assert len(set(outputs)) == 3
    
    def test_error_handling(self):
        """Test CLI error handling."""
        # Invalid text count
        result = self.runner.invoke(cli, ['text', '--count', '-1'])
        assert result.exit_code == 1
        assert "Error:" in result.output
        
        # Invalid password length
        result = self.runner.invoke(cli, ['password', '--length', '200'])
        assert result.exit_code == 1
        assert "Error:" in result.output
    
    def test_reproducibility_with_different_instances(self):
        """Test that different CLI invocations produce different results."""
        results = []
        for _ in range(5):
            result = self.runner.invoke(cli, ['password', '--length', '16'])
            assert result.exit_code == 0
            results.append(result.output.strip())
        
        # All passwords should be different
        assert len(set(results)) == 5