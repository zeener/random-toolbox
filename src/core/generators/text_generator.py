import secrets
import random
from typing import List, Literal

class TextGenerator:
    
    LOREM_WORDS = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
        "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
        "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
        "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
        "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
        "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
        "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
        "deserunt", "mollit", "anim", "id", "est", "laborum"
    ]
    
    def __init__(self):
        self._rng = random.Random(secrets.randbits(256))
    
    def generate_words(self, count: int = 10) -> List[str]:
        """Generate a list of random words."""
        if count <= 0:
            raise ValueError("Count must be positive")
        if count > 1000:
            raise ValueError("Count cannot exceed 1000")
            
        return [self._rng.choice(self.LOREM_WORDS) for _ in range(count)]
    
    def generate_sentence(self, word_count: int = None) -> str:
        """Generate a single sentence with random word count or specified count."""
        if word_count is None:
            word_count = self._rng.randint(8, 15)
        elif word_count <= 0 or word_count > 50:
            raise ValueError("Word count must be between 1 and 50")
            
        words = self.generate_words(word_count)
        sentence = " ".join(words).capitalize()
        return sentence + "."
    
    def generate_sentences(self, count: int = 5) -> List[str]:
        """Generate multiple sentences."""
        if count <= 0:
            raise ValueError("Count must be positive")
        if count > 100:
            raise ValueError("Count cannot exceed 100")
            
        return [self.generate_sentence() for _ in range(count)]
    
    def generate_paragraph(self, sentence_count: int = None) -> str:
        """Generate a paragraph with random or specified sentence count."""
        if sentence_count is None:
            sentence_count = self._rng.randint(4, 8)
        elif sentence_count <= 0 or sentence_count > 20:
            raise ValueError("Sentence count must be between 1 and 20")
            
        sentences = self.generate_sentences(sentence_count)
        return " ".join(sentences)
    
    def generate_paragraphs(self, count: int = 3) -> List[str]:
        """Generate multiple paragraphs."""
        if count <= 0:
            raise ValueError("Count must be positive")
        if count > 50:
            raise ValueError("Count cannot exceed 50")
            
        return [self.generate_paragraph() for _ in range(count)]
    
    def generate(self, 
                content_type: Literal["word", "sentence", "paragraph"] = "paragraph",
                count: int = 1) -> str | List[str]:
        """Main generation method with type selection."""
        
        if content_type == "word":
            result = self.generate_words(count)
            return result if count > 1 else result[0]
        elif content_type == "sentence":
            result = self.generate_sentences(count)
            return result if count > 1 else result[0]
        elif content_type == "paragraph":
            result = self.generate_paragraphs(count)
            return result if count > 1 else result[0]
        else:
            raise ValueError(f"Invalid content_type: {content_type}")