import sys
import pathlib
import pytest

# Ensure project root is on sys.path so tests can import application packages
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from core.config import settings
from main import create_app


@pytest.fixture(scope="session")
def test_db():
    # Use a persistent test database file located at the repository root.
    db_file = ROOT / "test_db.sqlite3"
    # Point the application to the persistent SQLite file for tests
    settings.DATABASE_URI = f"sqlite+aiosqlite:///{db_file}"
    return db_file


@pytest.fixture
def app(test_db):
    # Create the FastAPI app using the test database settings
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client
