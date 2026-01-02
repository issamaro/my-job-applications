import os
import tempfile
import pytest
from fastapi.testclient import TestClient

import database
from main import app


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a fresh database for each test using a temp file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    original_db = database.DATABASE
    database.DATABASE = path
    database.init_db()
    yield
    database.DATABASE = original_db
    os.unlink(path)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)
