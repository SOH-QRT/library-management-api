"""
In-memory application storage.

Assignment 1 does not require database persistence, so Books and
Members live in simple dictionaries for the lifetime of the running
process. Both routers import from this module so they share the same
data — this is what lets Book creation check for an existing Member,
and lets deleting a Member check for that Member's Books.

Assignment 2 will replace this module with SQLAlchemy models and a
real database; the in-memory shape here is deliberately simple so
that swap is easier later.
"""

from app.schemas.books import BookResponse
from app.schemas.members import MemberResponse

# --- Members ---
members_db: dict[int, MemberResponse] = {}
_next_member_id = 1


def get_next_member_id() -> int:
    global _next_member_id
    new_id = _next_member_id
    _next_member_id += 1
    return new_id


# --- Books ---
books_db: dict[int, BookResponse] = {}
_next_book_id = 1


def get_next_book_id() -> int:
    global _next_book_id
    new_id = _next_book_id
    _next_book_id += 1
    return new_id
