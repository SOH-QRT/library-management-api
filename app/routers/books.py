from fastapi import APIRouter, HTTPException, status

from app.schemas.books import BookCreate, BookResponse
from app.storage import books_db, get_next_book_id, members_db

router = APIRouter(prefix="/books", tags=["Books"])


def _ensure_member_exists(member_id: int) -> None:
    """Shared guard: a Book must reference a Member that actually
    exists. Raises 404 if it doesn't."""
    if member_id not in members_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} was not found. A Book must reference an existing Member.",
        )


def _ensure_isbn_unique(isbn: str, exclude_book_id: int | None = None) -> None:
    """Shared guard: ISBN must be unique across all Books. When
    updating, exclude_book_id lets a Book keep its own ISBN."""
    for existing_id, existing in books_db.items():
        if exclude_book_id is not None and existing_id == exclude_book_id:
            continue
        if existing.isbn == isbn:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A book with ISBN '{isbn}' already exists.",
            )


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Book",
)
def create_book(book: BookCreate) -> BookResponse:
    """Create a Book. Rejects a missing parent Member or a duplicate ISBN."""
    _ensure_member_exists(book.member_id)
    _ensure_isbn_unique(book.isbn)

    new_id = get_next_book_id()
    new_book = BookResponse(id=new_id, **book.model_dump())
    books_db[new_id] = new_book
    return new_book


@router.get(
    "",
    response_model=list[BookResponse],
    summary="Retrieve all Books",
)
def list_books() -> list[BookResponse]:
    return list(books_db.values())


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Retrieve one Book by id",
)
def get_book(book_id: int) -> BookResponse:
    book = books_db.get(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} was not found.",
        )
    return book


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update an existing Book",
)
def update_book(book_id: int, updated: BookCreate) -> BookResponse:
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} was not found.",
        )

    _ensure_member_exists(updated.member_id)
    _ensure_isbn_unique(updated.isbn, exclude_book_id=book_id)

    saved = BookResponse(id=book_id, **updated.model_dump())
    books_db[book_id] = saved
    return saved


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an existing Book",
)
def delete_book(book_id: int) -> None:
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} was not found.",
        )
    del books_db[book_id]
    return None
