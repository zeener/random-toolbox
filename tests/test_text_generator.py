import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.core.generators.text_generator import TextGenerator


class TestTextGenerator:
    
    def setup_method(self):
        """Setup for each test method."""
        self.generator = TextGenerator()
    
    def test_generate_words_default(self):
        """Test default word generation."""
        words = self.generator.generate_words()
        assert len(words) == 10
        assert all(isinstance(word, str) for word in words)
        assert all(word in self.generator.LOREM_WORDS for word in words)
    
    def test_generate_words_custom_count(self):
        """Test word generation with custom count."""
        words = self.generator.generate_words(5)
        assert len(words) == 5
        
        words = self.generator.generate_words(1)
        assert len(words) == 1
    
    def test_generate_words_invalid_count(self):
        """Test word generation with invalid counts."""
        with pytest.raises(ValueError, match="Count must be positive"):
            self.generator.generate_words(0)
            
        with pytest.raises(ValueError, match="Count must be positive"):
            self.generator.generate_words(-1)
            
        with pytest.raises(ValueError, match="Count cannot exceed 1000"):
            self.generator.generate_words(1001)
    
    def test_generate_sentence_default(self):
        """Test default sentence generation."""
        sentence = self.generator.generate_sentence()
        assert isinstance(sentence, str)
        assert sentence.endswith('.')
        assert sentence[0].isupper()  # Should be capitalized
        
        # Count words (split by space, remove period)
        words = sentence[:-1].split()
        assert 8 <= len(words) <= 15
    
    def test_generate_sentence_custom_word_count(self):
        """Test sentence generation with custom word count."""
        sentence = self.generator.generate_sentence(10)
        words = sentence[:-1].split()
        assert len(words) == 10
    
    def test_generate_sentence_invalid_word_count(self):
        """Test sentence generation with invalid word counts."""
        with pytest.raises(ValueError, match="Word count must be between 1 and 50"):
            self.generator.generate_sentence(0)
            
        with pytest.raises(ValueError, match="Word count must be between 1 and 50"):
            self.generator.generate_sentence(51)
    
    def test_generate_sentences(self):
        """Test multiple sentence generation."""
        sentences = self.generator.generate_sentences(3)
        assert len(sentences) == 3
        assert all(isinstance(s, str) for s in sentences)
        assert all(s.endswith('.') for s in sentences)
    
    def test_generate_sentences_invalid_count(self):
        """Test sentence generation with invalid counts."""
        with pytest.raises(ValueError, match="Count must be positive"):
            self.generator.generate_sentences(0)
            
        with pytest.raises(ValueError, match="Count cannot exceed 100"):
            self.generator.generate_sentences(101)
    
    def test_generate_paragraph_default(self):
        """Test default paragraph generation."""
        paragraph = self.generator.generate_paragraph()
        assert isinstance(paragraph, str)
        
        # Should contain multiple sentences
        sentence_count = paragraph.count('.')
        assert 4 <= sentence_count <= 8
    
    def test_generate_paragraph_custom_sentence_count(self):
        """Test paragraph generation with custom sentence count."""
        paragraph = self.generator.generate_paragraph(5)
        sentence_count = paragraph.count('.')
        assert sentence_count == 5
    
    def test_generate_paragraphs(self):
        """Test multiple paragraph generation."""
        paragraphs = self.generator.generate_paragraphs(2)
        assert len(paragraphs) == 2
        assert all(isinstance(p, str) for p in paragraphs)
    
    def test_generate_paragraphs_invalid_count(self):
        """Test paragraph generation with invalid counts."""
        with pytest.raises(ValueError, match="Count must be positive"):
            self.generator.generate_paragraphs(0)
            
        with pytest.raises(ValueError, match="Count cannot exceed 50"):
            self.generator.generate_paragraphs(51)
    
    def test_generate_main_method_word(self):
        """Test main generate method for words."""
        result = self.generator.generate("word", 1)
        assert isinstance(result, str)
        assert result in self.generator.LOREM_WORDS
        
        result = self.generator.generate("word", 3)
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_generate_main_method_sentence(self):
        """Test main generate method for sentences."""
        result = self.generator.generate("sentence", 1)
        assert isinstance(result, str)
        assert result.endswith('.')
        
        result = self.generator.generate("sentence", 2)
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_generate_main_method_paragraph(self):
        """Test main generate method for paragraphs."""
        result = self.generator.generate("paragraph", 1)
        assert isinstance(result, str)
        assert '.' in result  # Should contain sentences
        
        result = self.generator.generate("paragraph", 2)
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_generate_invalid_type(self):
        """Test main generate method with invalid type."""
        with pytest.raises(ValueError, match="Invalid content_type"):
            self.generator.generate("invalid_type", 1)
    
    def test_randomness(self):
        """Test that generation produces different results."""
        words1 = self.generator.generate_words(10)
        words2 = self.generator.generate_words(10)
        
        # Should be different (extremely unlikely to be identical)
        assert words1 != words2
    
    def test_lorem_words_content(self):
        """Test that LOREM_WORDS contains expected content."""
        assert len(self.generator.LOREM_WORDS) > 50
        assert "lorem" in self.generator.LOREM_WORDS
        assert "ipsum" in self.generator.LOREM_WORDS
        assert all(isinstance(word, str) for word in self.generator.LOREM_WORDS)