"""
Test configuration and shared fixtures.

Uses an in-memory SQLite database so tests run without Docker/Postgres.
Each test gets a clean database via function-scoped fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db: Session) -> TestClient:
    """FastAPI test client with the DB dependency overridden."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Register a user and return a valid Authorization header."""
    client.post("/auth/register", json={"email": "test@example.com", "password": "testpassword"})
    resp = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
