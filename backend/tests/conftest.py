"""Pytest fixtures shared across all test modules.

The test database is created in PostgreSQL once per session and wiped between
tests via SQLAlchemy transactions that are rolled back after each test function.
This keeps tests fast and fully isolated.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Override the DATABASE_URL before the app module loads its Settings.
# The CI workflow sets this; locally it falls back to a sensible default.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://bizreg_test:test_password@localhost:5432/bizreg_test",
)
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_tests_only_never_use_in_production")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.db.session import Base, get_db          # noqa: E402  (must follow env setup)
from app.main import app                          # noqa: E402
from app.core.security import hash_password       # noqa: E402
from app.models.role import Role                  # noqa: E402
from app.models.user import User                  # noqa: E402
from app.models.service import Service            # noqa: E402

TEST_DB_URL = os.environ["DATABASE_URL"]

# One engine for the whole test session — migrations are applied once.
engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Run Alembic migrations once before any test, then tear down the schema."""
    import subprocess
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        check=True,
    )
    yield
    # Drop everything so the next run starts clean.
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db() -> Session:
    """Provide a database session that is rolled back after every test.

    Rolling back instead of truncating is faster and avoids re-seeding reference
    data after each test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db: Session) -> TestClient:
    """FastAPI test client wired to the rollback-protected database session."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Reusable account fixtures ────────────────────────────────────────────────

def _make_user(db: Session, email: str, role_name: str, full_name: str = "Test User") -> User:
    role = db.query(Role).filter(Role.name == role_name).first()
    assert role is not None, f"Role '{role_name}' not seeded"
    user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password("StrongPassword1234"),
        role=role,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture()
def citizen_user(db: Session) -> User:
    return _make_user(db, "citizen@example.com", "citizen", "Citizen User")


@pytest.fixture()
def officer_user(db: Session) -> User:
    return _make_user(db, "officer@example.com", "officer", "Officer User")


@pytest.fixture()
def admin_user(db: Session) -> User:
    return _make_user(db, "admin@example.com", "admin", "Admin User")


@pytest.fixture()
def citizen_token(client: TestClient, citizen_user: User) -> str:
    """Register and log in a fresh citizen; return the access token."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": citizen_user.email, "password": "StrongPassword1234"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def officer_token(client: TestClient, officer_user: User) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": officer_user.email, "password": "StrongPassword1234"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def biz_reg_service(db: Session) -> Service:
    """Return the seeded business-registration service."""
    service = db.query(Service).filter(Service.code == "business-registration").first()
    assert service is not None, "Service 'business-registration' not seeded"
    return service
