"""
Configuration management for livelib-backup.
Centralized configuration with validation.
"""
from dataclasses import dataclass, field
from typing import Optional, List
import os


@dataclass
class BackupConfig:
    """Configuration for backup operations."""
    
    # Required
    username: str
    
    # File paths
    books_file: Optional[str] = None
    quotes_file: Optional[str] = None
    
    # Delay settings (seconds between requests)
    min_delay: float = 1.0
    max_delay: float = 3.0
    
    # Page limits
    read_count: Optional[int] = None
    quote_count: Optional[int] = None
    
    # Behavior flags
    rewrite_all: bool = False
    driver_type: str = "requests"  # "requests" or "selenium"
    
    # Skip options
    skip_books: bool = False
    skip_quotes: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        errors = self.validate()
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.username or not self.username.strip():
            errors.append("Username is required")
        
        if self.min_delay < 0.5:
            errors.append("min_delay too low (< 0.5s). Risk of being banned by LiveLib")
        
        if self.max_delay < self.min_delay:
            errors.append("max_delay must be >= min_delay")
        
        if self.driver_type not in ("requests", "selenium"):
            errors.append("driver_type must be 'requests' or 'selenium'")
        
        if self.read_count is not None and self.read_count < 1:
            errors.append("read_count must be >= 1")
        
        if self.quote_count is not None and self.quote_count < 1:
            errors.append("quote_count must be >= 1")
        
        return errors
    
    def get_books_file_path(self) -> str:
        """Get resolved books file path."""
        if self.books_file:
            return self.books_file
        return f"backup_{self.username}_book.csv"
    
    def get_quotes_file_path(self) -> str:
        """Get resolved quotes file path."""
        if self.quotes_file:
            return self.quotes_file
        return f"backup_{self.username}_quote.csv"
    
    def get_user_href(self) -> str:
        """Get full user profile URL."""
        return f"https://www.livelib.ru/reader/{self.username}"
