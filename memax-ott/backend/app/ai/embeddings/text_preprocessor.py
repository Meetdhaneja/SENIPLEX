"""
Text Preprocessor for AI Embeddings
Handles text cleaning, normalization, and preprocessing for movie/user data
"""

import re
import string
from typing import List, Optional
import unicodedata


class TextPreprocessor:
    """Preprocesses text data for embedding generation"""
    
    def __init__(
        self,
        lowercase: bool = True,
        remove_punctuation: bool = False,
        remove_numbers: bool = False,
        remove_extra_spaces: bool = True,
        max_length: Optional[int] = 512
    ):
        """
        Initialize text preprocessor
        
        Args:
            lowercase: Convert text to lowercase
            remove_punctuation: Remove punctuation marks
            remove_numbers: Remove numeric characters
            remove_extra_spaces: Remove extra whitespace
            max_length: Maximum text length (for truncation)
        """
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.remove_extra_spaces = remove_extra_spaces
        self.max_length = max_length
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess a single text string
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove punctuation
        if self.remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove numbers
        if self.remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Remove extra spaces
        if self.remove_extra_spaces:
            text = ' '.join(text.split())
        
        # Truncate to max length
        if self.max_length and len(text) > self.max_length:
            text = text[:self.max_length]
        
        return text.strip()
    
    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Preprocess a batch of text strings
        
        Args:
            texts: List of input texts
            
        Returns:
            List of preprocessed texts
        """
        return [self.preprocess(text) for text in texts]
    
    def clean_movie_text(self, title: str, description: str, genres: str) -> str:
        """
        Clean and combine movie metadata for embedding
        
        Args:
            title: Movie title
            description: Movie description
            genres: Movie genres (comma-separated)
            
        Returns:
            Combined and cleaned text
        """
        # Combine all fields
        combined = f"{title}. {description}. Genres: {genres}"
        
        # Preprocess
        return self.preprocess(combined)
    
    def clean_user_text(self, preferences: List[str], history: List[str]) -> str:
        """
        Clean and combine user data for embedding
        
        Args:
            preferences: User preference tags
            history: User viewing history titles
            
        Returns:
            Combined and cleaned text
        """
        # Combine preferences and history
        pref_text = " ".join(preferences) if preferences else ""
        history_text = " ".join(history) if history else ""
        
        combined = f"Preferences: {pref_text}. History: {history_text}"
        
        # Preprocess
        return self.preprocess(combined)
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """
        Remove HTML tags from text
        
        Args:
            text: Text with potential HTML tags
            
        Returns:
            Text without HTML tags
        """
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """
        Remove URLs from text
        
        Args:
            text: Text with potential URLs
            
        Returns:
            Text without URLs
        """
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub('', text)
    
    @staticmethod
    def remove_special_characters(text: str, keep_spaces: bool = True) -> str:
        """
        Remove special characters from text
        
        Args:
            text: Input text
            keep_spaces: Whether to keep spaces
            
        Returns:
            Text without special characters
        """
        if keep_spaces:
            pattern = r'[^a-zA-Z0-9\s]'
        else:
            pattern = r'[^a-zA-Z0-9]'
        
        return re.sub(pattern, '', text)


# Default preprocessor instance
default_preprocessor = TextPreprocessor(
    lowercase=True,
    remove_punctuation=False,
    remove_numbers=False,
    remove_extra_spaces=True,
    max_length=512
)


def preprocess_text(text: str) -> str:
    """
    Convenience function for quick text preprocessing
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    return default_preprocessor.preprocess(text)
