from fastapi import APIRouter, HTTPException, status

from app.schemas.books import BookResponse
from app.schemas.members import MemberCreate, MemberResponse
from app.storage import books_db, get_next_member_id, members_db

router = APIRouter(prefix="/members", tags=["Members"])


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Member",
)
def create_member(member: MemberCreate) -> MemberResponse:
    """Create a Member. Rejects duplicate email or membership_id."""
    for existing in members_db.values():
        if existing.email == member.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A member with email '{member.email}' already exists.",
            )
        if existing.membership_id == member.membership_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A member with membership_id '{member.membership_id}' already exists.",
            )

    new_id = get_next_member_id()
    new_member = MemberResponse(id=new_id, **member.model_dump())
    members_db[new_id] = new_member
    return new_member


@router.get(
    "",
    response_model=list[MemberResponse],
    summary="Retrieve all Members",
)
def list_members() -> list[MemberResponse]:
    return list(members_db.values())


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Retrieve one Member by id",
)
def get_member(member_id: int) -> MemberResponse:
    member = members_db.get(member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} was not found.",
        )
    return member


@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="Retrieve the Books associated with a Member",
)
def get_member_books(member_id: int) -> list[BookResponse]:
    if member_id not in members_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} was not found.",
        )
    return [book for book in books_db.values() if book.member_id == member_id]


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update an existing Member",
)
def update_member(member_id: int, updated: MemberCreate) -> MemberResponse:
    if member_id not in members_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} was not found.",
        )

    # Check email/membership_id uniqueness against every OTHER member
    # (excluding this one, since it's allowed to keep its own values).
    for other_id, existing in members_db.items():
        if other_id == member_id:
            continue
        if existing.email == updated.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A member with email '{updated.email}' already exists.",
            )
        if existing.membership_id == updated.membership_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A member with membership_id '{updated.membership_id}' already exists.",
            )

    saved = MemberResponse(id=member_id, **updated.model_dump())
    members_db[member_id] = saved
    return saved


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an existing Member",
)
def delete_member(member_id: int) -> None:
    if member_id not in members_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} was not found.",
        )

    # A Member with existing Books cannot be deleted. Those Books must
    # first be deleted or reassigned to another Member.
    has_books = any(book.member_id == member_id for book in books_db.values())
    if has_books:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Member {member_id} still has associated Books and cannot "
                "be deleted. Delete or reassign those Books first."
            ),
        )

    del members_db[member_id]
    return None
