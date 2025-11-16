import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Default to SQLite if not specified
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///pizzagpt.db")

# For SQLite, you need check_same_thread=False for multithreading (FastMCP may use threads)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
else:
    # Example: postgresql+psycopg://user:password@localhost:5432/pizzagpt
    engine = create_engine(DATABASE_URL, echo=True)


def get_engine():
    """Return the SQLModel engine."""
    return engine


def init_db():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created.")


def get_session() -> Session:
    """Context manager for creating DB sessions."""
    return Session(engine)
