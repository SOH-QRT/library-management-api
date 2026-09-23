from fastapi import FastAPI

from app.routers.books import router as books_router
from app.routers.members import router as members_router

# Create the FastAPI application object that Uvicorn will load and run.
# This metadata is also displayed in the generated API documentation.
app = FastAPI(
    title="Library Management System API",
    description="An API for managing Books and Members in a library.",
    version="0.1.0",
)


@app.get("/", tags=["General"], summary="API welcome message")
def read_root() -> dict[str, str]:
    """Greet visitors and point them toward the interactive docs."""
    return {
        "message": "Welcome to the Library Management System API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["General"], summary="Check API health")
def health_check() -> dict[str, str]:
    """Confirm that the API process is running."""
    return {"status": "healthy"}


# Add every Book route defined in app/routers/books.py to the application.
app.include_router(books_router)

# Add every Member route defined in app/routers/members.py to the application.
app.include_router(members_router)
