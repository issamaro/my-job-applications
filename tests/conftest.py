import os

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

import json
import tempfile
import pytest
from fastapi.testclient import TestClient

import database
import settings
from main import app


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a fresh database for each test using a temp file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    original_db = settings.DATABASE
    settings.DATABASE = path
    database.init_db()
    yield
    settings.DATABASE = original_db
    os.unlink(path)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def create_llm_result(parsed, **breadcrumb_overrides):
    """Wrap a parsed LLM dict into the (parsed, breadcrumbs) tuple shape returned
    by LLMProvider.analyze_and_generate. Tests that need to assert on breadcrumb
    fields pass overrides; the defaults cover the rest with sentinel values.
    """
    breadcrumbs = {
        "provider": "claude",
        "model": "claude-test-model",
        "prompt_path": "services/llm/base.py:SYSTEM_PROMPT",
        "prompt_hash": "a" * 40,
        "raw_output": json.dumps(parsed),
        "latency_ms": 42,
        "input_tokens": 1000,
        "output_tokens": 500,
        "profile_snapshot": "{}",
    }
    breadcrumbs.update(breadcrumb_overrides)
    return parsed, breadcrumbs
