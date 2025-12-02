from typing import Optional, List
from .book import Book
from .utils import handle_none, add_livelib


class Quote:
    """Represents a quote from a book on Livelib."""

    def __init__(self, link: str, text: str, book: Book = None) -> None:
        self.link: str = add_livelib(handle_none(link))
        self.text: str = handle_none(text)
        self.book: Book = book if book is not None else Book()

    def __str__(self) -> str:
        return '%s\t%s\t%s\t%s\t%s' % (self.book.name, self.book.author, self.text, self.book.link, self.link)

    def __eq__(self, other: object) -> bool:
        """Check equality based on quote link."""
        if not isinstance(other, Quote):
            return NotImplemented
        return self.link == other.link

    def __ne__(self, other: object) -> bool:
        """Check inequality based on quote link."""
        if not isinstance(other, Quote):
            return NotImplemented
        return self.link != other.link

    def __hash__(self) -> int:
        """Make Quote hashable for use in sets/dicts."""
        return hash(self.link)

    def to_list(self) -> List[str]:
        """Convert quote data to list format."""
        return list(self.__dict__.values())

    def add_book(self, book: Book) -> None:
        """Update associated book."""
        self.book = book
