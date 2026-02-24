"""
Book data model with validation.
"""
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class Book:
    """Represents a book from LiveLib."""
    
    link: str
    status: str
    name: Optional[str] = None
    author: Optional[str] = None
    rating: Optional[str] = None
    date: Optional[str] = None
    
    def __post_init__(self):
        """Validate book data after initialization."""
        if not self._is_valid_link():
            raise ValueError(f"Invalid book link: {self.link}")
        
        valid_statuses = ('read', 'reading', 'wish')
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status '{self.status}'. Must be one of: {valid_statuses}")
    
    def _is_valid_link(self) -> bool:
        """Validate book link format."""
        if not self.link:
            return False
        try:
            parsed = urlparse(self.link)
            return parsed.scheme in ('http', 'https') and ('/book/' in self.link or '/work/' in self.link)
        except Exception:
            return False
    
    def __str__(self) -> str:
        """Convert book to CSV row format."""
        return f"{self.name or ''}\t{self.author or ''}\t{self.status}\t{self.rating or ''}\t{self.date or ''}\t{self.link}"
    
    def __eq__(self, other) -> bool:
        """Check equality based on link."""
        if not isinstance(other, Book):
            return False
        return self.link == other.link
    
    def __hash__(self) -> int:
        """Hash based on link for set operations."""
        return hash(self.link)
