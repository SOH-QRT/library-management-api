import re

from pydantic import BaseModel, EmailStr, Field, field_validator

# Phone numbers must be entered in the format XXX-XXX-XXXX (US-style,
# hyphen-separated). This is a deliberately simple, documented rule —
# it does not validate area codes or real-world phone number ranges.
PHONE_PATTERN = re.compile(r"^\d{3}-\d{3}-\d{4}$")


class MemberBase(BaseModel):
    """Fields shared between create and update requests."""

    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    membership_id: str = Field(..., min_length=1)
    phone: str

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        # Trim whitespace, then re-check length so " " alone can't pass.
        trimmed = value.strip()
        if not (1 <= len(trimmed) <= 120):
            raise ValueError("name must be 1-120 characters after trimming")
        return trimmed

    @field_validator("membership_id")
    @classmethod
    def trim_membership_id(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("membership_id cannot be blank")
        return trimmed

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        # Required format: XXX-XXX-XXXX (e.g. 555-123-4567).
        if not PHONE_PATTERN.match(value):
            raise ValueError("phone must be in the format XXX-XXX-XXXX")
        return value


class MemberCreate(MemberBase):
    """Request body for creating or updating a Member. No id — the
    application generates it."""

    pass


class MemberResponse(MemberBase):
    """Response body returned to clients. Includes the generated id."""

    id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Jordan Lee",
                    "email": "jordan.lee@example.com",
                    "membership_id": "MEM-1001",
                    "phone": "555-123-4567",
                }
            ]
        }
    }
