# Library Management System API

A REST API for managing Library **Books** and **Members**, built with
FastAPI. This is Assignment 1 for SDEV 3310 (API Design and
Development) — it implements full CRUD for both resources, a
one-to-many Member-to-Books relationship, request/response validation,
and an auto-generated OpenAPI contract.

## Project purpose

Library staff need a way to track which Books are currently checked
out and by which Member. This API supports:

- Creating, viewing, updating, and deleting Book records
- Creating, viewing, updating, and deleting Member records
- Associating each Book with exactly one Member
- Retrieving every Book currently associated with a given Member
- Preventing data integrity issues — duplicate ISBNs, duplicate Member
  emails/membership IDs, Books referencing a Member that doesn't
  exist, and deleting a Member who still has Books checked out

> **Note:** This milestone uses simple in-memory, application-level
> storage. Data resets every time the server restarts. Database
> persistence (SQLAlchemy) is introduced in Assignment 2.

## Getting started

### Prerequisites

- Python 3.12+ (or whatever version your `.python-version` specifies)
- [`uv`](https://docs.astral.sh/uv/) for dependency management

### Installation

Clone the repository and check out the `assignment-1` branch:

```bash
git clone https://github.com/SOH-QRT/library-management-api.git
cd library-management-api
git checkout assignment-1
```

Install dependencies (this reads `pyproject.toml` / `uv.lock` and
creates a virtual environment automatically):

```bash
uv sync
```

### Running the server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Interactive documentation

Once the server is running, the OpenAPI contract is available at:

- **Swagger UI (interactive):** http://127.0.0.1:8000/docs
- **ReDoc (reference-style):** http://127.0.0.1:8000/redoc
- **Raw OpenAPI JSON:** http://127.0.0.1:8000/openapi.json

Swagger UI lets you execute real requests against the running API
directly from the browser — this is the fastest way to explore the
endpoints below.

## Example requests

### Create a Member

`POST /members`

```json
{
  "name": "Jordan Lee",
  "email": "jordan@example.com",
  "membership_id": "MEM-1001",
  "phone": "555-123-4567"
}
```

Response — `201 Created`:

```json
{
  "id": 1,
  "name": "Jordan Lee",
  "email": "jordan@example.com",
  "membership_id": "MEM-1001",
  "phone": "555-123-4567"
}
```

> **Phone format:** `phone` must match `XXX-XXX-XXXX` (digits and
> hyphens only, e.g. `555-123-4567`). Any other format is rejected
> with a `422 Unprocessable Entity` response.

### Create a Book for that Member

`POST /books`

```json
{
  "title": "The Pragmatic Programmer",
  "author": "David Thomas",
  "isbn": "978-0135957059",
  "published_year": 2019,
  "member_id": 1
}
```

Response — `201 Created`:

```json
{
  "id": 1,
  "title": "The Pragmatic Programmer",
  "author": "David Thomas",
  "isbn": "978-0135957059",
  "published_year": 2019,
  "member_id": 1
}
```

If `member_id` does not correspond to an existing Member, this
returns `404 Not Found`. If `isbn` already exists on another Book,
this returns `409 Conflict`.

### Retrieve the Books associated with a Member

`GET /members/1/books`

Response — `200 OK`:

```json
[
  {
    "id": 1,
    "title": "The Pragmatic Programmer",
    "author": "David Thomas",
    "isbn": "978-0135957059",
    "published_year": 2019,
    "member_id": 1
  }
]
```

### Attempt to delete a Member who still has Books

`DELETE /members/1`

Response — `409 Conflict`:

```json
{
  "detail": "Member 1 still has associated Books and cannot be deleted. Delete or reassign those Books first."
}
```

The Book must be deleted or reassigned to another Member before the
Member record can be deleted.

## All endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Welcome message with links to the docs |
| GET | `/health` | API health check |
| POST | `/members` | Create a Member |
| GET | `/members` | List all Members |
| GET | `/members/{member_id}` | Retrieve one Member |
| PUT | `/members/{member_id}` | Update a Member |
| DELETE | `/members/{member_id}` | Delete a Member (blocked if they have Books) |
| GET | `/members/{member_id}/books` | List a Member's Books |
| POST | `/books` | Create a Book |
| GET | `/books` | List all Books |
| GET | `/books/{book_id}` | Retrieve one Book |
| PUT | `/books/{book_id}` | Update a Book |
| DELETE | `/books/{book_id}` | Delete a Book |

## Validation rules

**Book**

- `title` — required, 1-200 characters after trimming
- `author` — required, 1-120 characters after trimming
- `isbn` — required, unique across all Books
- `published_year` — integer, between 1450 and the current year
- `member_id` — required, must reference an existing Member

**Member**

- `name` — required, 1-120 characters after trimming
- `email` — required, valid email format, unique across all Members
- `membership_id` — required, unique across all Members
- `phone` — required, must match `XXX-XXX-XXXX`

## Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app instance, root/health routes, router wiring
│   ├── storage.py             # Shared in-memory data store for Books and Members
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py           # Book CRUD endpoints
│   │   └── members.py         # Member CRUD endpoints + relationship endpoint
│   └── schemas/
│       ├── __init__.py
│       ├── books.py           # BookCreate / BookResponse Pydantic models
│       └── members.py         # MemberCreate / MemberResponse Pydantic models
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

## Notes on design decisions

- **Separate Create/Response schemas** — request bodies never include
  `id` (the application generates it); response bodies always do.
- **Uniqueness and relationship checks live in the routers, not the
  schemas** — Pydantic validates the shape of a single incoming
  request in isolation; it has no visibility into other stored
  records, so cross-record checks (duplicate ISBN, existing
  `member_id`) are handled in `app/routers/`.
- **`published_year`'s upper bound is computed at request time**
  (`datetime.now().year`), not hardcoded, so the rule stays correct
  without future code changes.
