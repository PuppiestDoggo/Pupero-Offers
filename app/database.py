from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Prefer generic DATABASE_URL (to align with other services), then OFFERS_DATABASE_URL, else fallback to sqlite
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("OFFERS_DATABASE_URL") or "sqlite:///./offers.db"

# For sqlite we need special connect args; for MariaDB/Postgres/etc, leave empty
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine (schema creation is centralized in CreateDB)
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    # No-op: schema is managed by CreateDB
    return None


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
