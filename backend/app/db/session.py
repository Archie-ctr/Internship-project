"""SQLAlchemy connection and request-session infrastructure.

`SessionLocal` is not used by API routes until a later phase, but defining it
now gives migrations and future dependencies one consistent database boundary.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """The parent class that collects table metadata for SQLAlchemy/Alembic."""


def get_db():
    """Provide one transaction-aware session per request and always close it.

    A route must depend on this generator instead of creating global sessions:
    that prevents connections leaking after errors and keeps each request's
    database work isolated.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
