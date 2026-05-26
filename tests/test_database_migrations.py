"""Tests for the additive breadcrumb-column migration on generated_resumes.

Covers three scenarios: fresh install adds the columns; init_db is idempotent;
the FK CASCADE recreate path carries the breadcrumb columns through.
"""

import sqlite3

import pytest

import database


_BREADCRUMB_COLUMNS = (
    "prompt_path",
    "prompt_hash",
    "provider",
    "model",
    "profile_snapshot",
    "raw_output",
    "latency_ms",
    "input_tokens",
    "output_tokens",
)


def test_fresh_install_includes_breadcrumb_columns(tmp_path, monkeypatch):
    db_path = tmp_path / "fresh.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    database.init_db()

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("PRAGMA table_info(generated_resumes)")
        columns = {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()

    for column in _BREADCRUMB_COLUMNS:
        assert column in columns, f"missing breadcrumb column on fresh install: {column}"


def test_init_db_idempotent_with_breadcrumb_columns(tmp_path, monkeypatch):
    db_path = tmp_path / "idempotent.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    database.init_db()
    conn = sqlite3.connect(db_path)
    first_columns = {row[1] for row in conn.execute("PRAGMA table_info(generated_resumes)").fetchall()}
    conn.close()

    database.init_db()
    conn = sqlite3.connect(db_path)
    second_columns = {row[1] for row in conn.execute("PRAGMA table_info(generated_resumes)").fetchall()}
    conn.close()

    assert first_columns == second_columns
    for column in _BREADCRUMB_COLUMNS:
        assert column in second_columns


def test_recreate_path_preserves_breadcrumb_columns(tmp_path, monkeypatch):
    """Forced pre-CASCADE → CASCADE migration must carry breadcrumb columns
    through the recreate, and existing rows must survive with NULL breadcrumbs."""
    db_path = tmp_path / "legacy.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT NOT NULL,
            parsed_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO job_descriptions (id, raw_text, parsed_data)
        VALUES (1, 'legacy JD', '{"skills":[]}');
        CREATE TABLE generated_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_description_id INTEGER NOT NULL,
            job_title TEXT,
            company_name TEXT,
            match_score REAL,
            resume_content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id)
        );
        INSERT INTO generated_resumes
        (job_description_id, job_title, resume_content)
        VALUES (1, 'Test Engineer', '{}');
    """)
    conn.commit()
    conn.close()

    database.init_db()

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
        )
        table_sql = cursor.fetchone()[0]
        assert "ON DELETE CASCADE" in table_sql

        columns = {row[1] for row in conn.execute("PRAGMA table_info(generated_resumes)").fetchall()}
        for column in _BREADCRUMB_COLUMNS:
            assert column in columns, f"missing breadcrumb column after recreate: {column}"

        row = conn.execute(
            "SELECT job_title, prompt_hash, provider FROM generated_resumes WHERE id = 1"
        ).fetchone()
        assert row[0] == "Test Engineer"
        assert row[1] is None
        assert row[2] is None
    finally:
        conn.close()
