"""
Quote data model with validation.
"""
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
from .book import Book


@dataclass
class Quote:
    """Represents a quote from LiveLib."""
    
    link: str
    text: str
    book: Book
    
    def __post_init__(self):
        """Validate quote data after initialization."""
        if not self._is_valid_link():
            raise ValueError(f"Invalid quote link: {self.link}")
        
        if not self.text or not self.text.strip():
            raise ValueError("Quote text cannot be empty")
        
        if not isinstance(self.book, Book):
            raise ValueError("book must be a Book instance")
    
    def _is_valid_link(self) -> bool:
        """Validate quote link format."""
        if not self.link:
            return False
        try:
            parsed = urlparse(self.link)
            return parsed.scheme in ('http', 'https') and '/quote/' in self.link
        except Exception:
            return False
    
    def __str__(self) -> str:
        """Convert quote to CSV row format."""
        return f"{self.book.name or ''}\t{self.book.author or ''}\t{self.text}\t{self.book.link}\t{self.link}"
    
    def __eq__(self, other) -> bool:
        """Check equality based on link."""
        if not isinstance(other, Quote):
            return False
        return self.link == other.link
    
    def __hash__(self) -> int:
        """Hash based on link for set operations."""
        return hash(self.link)
