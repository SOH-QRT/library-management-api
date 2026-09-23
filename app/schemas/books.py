from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class BookBase(BaseModel):
    """Fields shared between create and update requests."""

    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=120)
    isbn: str = Field(..., min_length=1)
    published_year: int
    # Identifies the existing Member who borrowed this Book. Only the
    # shape (a positive int) is validated here — confirming the
    # referenced Member actually exists happens in the router, since
    # a schema has no visibility into other stored records.
    member_id: int = Field(..., gt=0)

    @field_validator("title")
    @classmethod
    def trim_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not (1 <= len(trimmed) <= 200):
            raise ValueError("title must be 1-200 characters after trimming")
        return trimmed

    @field_validator("author")
    @classmethod
    def trim_author(cls, value: str) -> str:
        trimmed = value.strip()
        if not (1 <= len(trimmed) <= 120):
            raise ValueError("author must be 1-120 characters after trimming")
        return trimmed

    @field_validator("isbn")
    @classmethod
    def trim_isbn(cls, value: str) -> str:
        # Only whitespace-trims and checks for blank input here.
        # Uniqueness across existing Books is enforced in the router,
        # not here, since that requires knowledge of other records.
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("isbn cannot be blank")
        return trimmed

    @field_validator("published_year")
    @classmethod
    def validate_published_year(cls, value: int) -> int:
        # Upper bound is computed at validation time, not hardcoded,
        # so the rule stays correct in every future year.
        current_year = datetime.now().year
        if not (1450 <= value <= current_year):
            raise ValueError(f"published_year must be between 1450 and {current_year}")
        return value


class BookCreate(BookBase):
    """Request body for creating or updating a Book. No id — the
    application generates it."""

    pass


class BookResponse(BookBase):
    """Response body returned to clients. Includes the generated id."""

    id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "The Pragmatic Programmer",
                    "author": "David Thomas",
                    "isbn": "978-0135957059",
                    "published_year": 2019,
                    "member_id": 1,
                }
            ]
        }
    }
