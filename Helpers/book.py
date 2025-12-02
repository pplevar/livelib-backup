from typing import Optional, List
from .utils import handle_none, add_livelib


class Book:
    """Represents a book with metadata from Livelib."""

    def __init__(
        self,
        link: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        author: Optional[str] = None,
        rating: Optional[str] = None,
        date: Optional[str] = None
    ) -> None:
        self.name: str = handle_none(name)
        self.author: str = handle_none(author)
        self.status: str = handle_none(status)
        self.rating: str = handle_none(rating)
        self.date: str = handle_none(date)
        self.link: str = add_livelib(handle_none(link))

    def __str__(self) -> str:
        return '%s\t%s\t%s\t%s\t%s\t%s' % (self.name, self.author, self.status, self.rating, self.date, self.link)

    def __eq__(self, other: object) -> bool:
        """Check equality based on book link."""
        if not isinstance(other, Book):
            return NotImplemented
        return self.link == other.link

    def __ne__(self, other: object) -> bool:
        """Check inequality based on book link."""
        if not isinstance(other, Book):
            return NotImplemented
        return self.link != other.link

    def __hash__(self) -> int:
        """Make Book hashable for use in sets/dicts."""
        return hash(self.link)

    def to_list(self) -> List[str]:
        """Convert book data to list format."""
        return list(self.__dict__.values())

    def add_name(self, name: str) -> None:
        """Update book name."""
        self.name = name

    def add_author(self, author: str) -> None:
        """Update book author."""
        self.author = author
