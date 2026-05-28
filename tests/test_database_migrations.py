# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Tests for database.py — recreate helpers, MIGRATIONS runner, schema_versions, dead-table absence, source-tolerance.

import shutil
import sqlite3
import traceback
from contextlib import contextmanager
from pathlib import Path

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


def _read_table_info(conn, table):
    return {
        (row[1], row[2], row[3], row[4], row[5])
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }


def _read_explicit_indexes(conn, table):
    return {
        (row[1], row[2])
        for row in conn.execute(f"PRAGMA index_list({table})").fetchall()
        if row[3] == "c"
    }


def _read_index_columns(conn, index_name):
    return {
        row[2]
        for row in conn.execute(f"PRAGMA index_info({index_name})").fetchall()
    }


def _read_foreign_keys(conn, table):
    return {
        (row[3], row[2], row[4], row[6])
        for row in conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
    }


def _read_table_names(conn):
    return {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    }


def _check_pragma_equivalent(db_a_path, db_b_path):
    conn_a = sqlite3.connect(db_a_path)
    conn_b = sqlite3.connect(db_b_path)
    try:
        tables_a = _read_table_names(conn_a)
        tables_b = _read_table_names(conn_b)
        if tables_a != tables_b:
            return False, f"tables differ: {tables_a ^ tables_b}"
        for table in tables_a:
            cols_a = _read_table_info(conn_a, table)
            cols_b = _read_table_info(conn_b, table)
            if cols_a != cols_b:
                return False, f"columns differ on {table}: {cols_a ^ cols_b}"
            idx_a = _read_explicit_indexes(conn_a, table)
            idx_b = _read_explicit_indexes(conn_b, table)
            if idx_a != idx_b:
                return False, f"indexes differ on {table}: {idx_a ^ idx_b}"
            for index_name, _ in idx_a:
                cols_idx_a = _read_index_columns(conn_a, index_name)
                cols_idx_b = _read_index_columns(conn_b, index_name)
                if cols_idx_a != cols_idx_b:
                    return False, f"index columns differ on {index_name}"
            fks_a = _read_foreign_keys(conn_a, table)
            fks_b = _read_foreign_keys(conn_b, table)
            if fks_a != fks_b:
                return False, f"FKs differ on {table}: {fks_a ^ fks_b}"
        return True, "equivalent"
    finally:
        conn_a.close()
        conn_b.close()


def _read_table_shape(conn, table):
    return {
        (row[1], row[2], row[3], row[5])
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }


def _check_schema_shape_equivalent(db_a_path, db_b_path):
    conn_a = sqlite3.connect(db_a_path)
    conn_b = sqlite3.connect(db_b_path)
    try:
        tables_a = _read_table_names(conn_a)
        tables_b = _read_table_names(conn_b)
        if tables_a != tables_b:
            return False, f"tables differ: {tables_a ^ tables_b}"
        for table in tables_a:
            cols_a = _read_table_shape(conn_a, table)
            cols_b = _read_table_shape(conn_b, table)
            if cols_a != cols_b:
                return False, f"columns differ on {table}: {cols_a ^ cols_b}"
            idx_a = _read_explicit_indexes(conn_a, table)
            idx_b = _read_explicit_indexes(conn_b, table)
            if idx_a != idx_b:
                return False, f"indexes differ on {table}: {idx_a ^ idx_b}"
            for index_name, _ in idx_a:
                cols_idx_a = _read_index_columns(conn_a, index_name)
                cols_idx_b = _read_index_columns(conn_b, index_name)
                if cols_idx_a != cols_idx_b:
                    return False, f"index columns differ on {index_name}"
            fks_a = _read_foreign_keys(conn_a, table)
            fks_b = _read_foreign_keys(conn_b, table)
            if fks_a != fks_b:
                return False, f"FKs differ on {table}: {fks_a ^ fks_b}"
        return True, "equivalent"
    finally:
        conn_a.close()
        conn_b.close()


@contextmanager
def _capture_trace(conn):
    captured = []
    conn.set_trace_callback(captured.append)
    try:
        yield captured
    finally:
        conn.set_trace_callback(None)


def _count_calls(monkeypatch, attr_name):
    original = getattr(database, attr_name)
    counter = {"calls": 0}

    def wrapper(*args, **kwargs):
        counter["calls"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(database, attr_name, wrapper)
    return counter


def _write_legacy_2024(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE personal_info (
            id INTEGER PRIMARY KEY DEFAULT 1,
            full_name TEXT NOT NULL, email TEXT NOT NULL,
            phone TEXT, location TEXT, linkedin_url TEXT, summary TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            CHECK (id = 1)
        );
        CREATE TABLE work_experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL, title TEXT NOT NULL,
            start_date TEXT NOT NULL, end_date TEXT,
            is_current INTEGER DEFAULT 0, description TEXT, location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution TEXT NOT NULL, degree TEXT NOT NULL,
            field_of_study TEXT, graduation_year INTEGER, gpa REAL, notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, description TEXT, technologies TEXT, url TEXT,
            start_date TEXT, end_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL CHECK(level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
            display_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT NOT NULL, parsed_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE generated_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_description_id INTEGER NOT NULL,
            job_title TEXT, company_name TEXT, match_score REAL,
            resume_content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id)
        );
        CREATE INDEX idx_generated_resumes_created ON generated_resumes(created_at DESC);
        INSERT INTO personal_info (id, full_name, email, phone, summary)
            VALUES (1, 'Legacy User', 'legacy@example.com', '555-0100', 'old');
        INSERT INTO job_descriptions (id, raw_text)
            VALUES (1, 'Legacy job description text');
        INSERT INTO generated_resumes (job_description_id, job_title, resume_content)
            VALUES (1, 'Legacy Engineer', '{}');
    """)
    conn.commit()
    conn.close()


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


def test_fresh_install_skips_recreates_and_seeds_versions(tmp_path, monkeypatch):
    db_path = tmp_path / "fresh.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    skills_counter = _count_calls(monkeypatch, "_migrate_skills_unique_constraint")
    gr_counter = _count_calls(monkeypatch, "_migrate_generated_resumes_fk_cascade")

    database.init_db()

    assert skills_counter["calls"] == 1
    assert gr_counter["calls"] == 1

    conn = sqlite3.connect(db_path)
    try:
        gr_sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
        ).fetchone()[0]
        assert "ON DELETE CASCADE" in gr_sql

        skills_sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='skills'"
        ).fetchone()[0]
        assert "UNIQUE(user_id, name)" in skills_sql

        version_count = conn.execute("SELECT COUNT(*) FROM schema_versions").fetchone()[0]
        assert version_count == len(database.MIGRATIONS)
    finally:
        conn.close()


def test_upgrade_path_matches_fresh_install(tmp_path, monkeypatch):
    legacy_path = tmp_path / "legacy.db"
    fresh_path = tmp_path / "fresh.db"

    _write_legacy_2024(legacy_path)

    monkeypatch.setattr(database, "DATABASE", str(legacy_path))
    database.init_db()

    monkeypatch.setattr(database, "DATABASE", str(fresh_path))
    database.init_db()

    equivalent, message = _check_pragma_equivalent(str(legacy_path), str(fresh_path))
    assert equivalent, message


def test_init_db_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "idempotent.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    database.init_db()

    before_versions = sqlite3.connect(db_path).execute(
        "SELECT COUNT(*) FROM schema_versions"
    ).fetchone()[0]

    conn_for_trace = sqlite3.connect(db_path)
    captured = []
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    original_get_db = database.get_db

    @contextmanager
    def get_db_with_trace():
        with original_get_db() as conn:
            conn.set_trace_callback(captured.append)
            try:
                yield conn
            finally:
                conn.set_trace_callback(None)

    monkeypatch.setattr(database, "get_db", get_db_with_trace)

    database.init_db()

    after_versions = sqlite3.connect(db_path).execute(
        "SELECT COUNT(*) FROM schema_versions"
    ).fetchone()[0]

    joined = "\n".join(captured)
    assert "ALTER TABLE" not in joined
    assert "_new" not in joined
    assert before_versions == after_versions

    conn_for_trace.close()


def test_recreate_preserves_extra_columns(tmp_path, monkeypatch):
    db_path = tmp_path / "extra.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            parsed_data TEXT
        );
        INSERT INTO jobs (id, original_text) VALUES (1, 'job for fk');
        CREATE TABLE generated_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            job_title TEXT,
            resume_content TEXT NOT NULL,
            experimental_field TEXT DEFAULT 'preserved',
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        );
        INSERT INTO generated_resumes (job_id, job_title, resume_content, experimental_field)
        VALUES (1, 'Test', '{}', 'this-should-survive');
    """)
    conn.commit()

    database._migrate_generated_resumes_fk_cascade(conn)

    columns = {row[1] for row in conn.execute("PRAGMA table_info(generated_resumes)").fetchall()}
    assert "experimental_field" in columns

    row = conn.execute(
        "SELECT experimental_field FROM generated_resumes WHERE id = 1"
    ).fetchone()
    assert row[0] == "this-should-survive"

    table_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
    ).fetchone()[0]
    assert "ON DELETE CASCADE" in table_sql

    conn.close()


def test_failing_migration_fails_loud(tmp_path, monkeypatch):
    db_path = tmp_path / "broken.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    broken_migrations = list(database.MIGRATIONS) + [
        ("20999999_broken", "ALTER TABLE doesnotexist ADD COLUMN x TEXT"),
    ]
    monkeypatch.setattr(database, "MIGRATIONS", broken_migrations)

    with pytest.raises(sqlite3.OperationalError) as exc_info:
        database.init_db()

    rendered = "".join(
        traceback.format_exception(type(exc_info.value), exc_info.value, exc_info.value.__traceback__)
    )
    assert "20999999_broken" in rendered

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM schema_versions WHERE version='20999999_broken'"
        ).fetchone()
        assert row[0] == 0
    finally:
        conn.close()


def test_seeds_schema_versions_for_upgraded_db(tmp_path, monkeypatch):
    db_path = tmp_path / "upgraded.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    database.init_db()

    drop_conn = sqlite3.connect(db_path)
    drop_conn.execute("DROP TABLE schema_versions")
    drop_conn.commit()
    drop_conn.close()

    captured = []
    original_get_db = database.get_db

    @contextmanager
    def get_db_with_trace():
        with original_get_db() as conn:
            conn.set_trace_callback(captured.append)
            try:
                yield conn
            finally:
                conn.set_trace_callback(None)

    monkeypatch.setattr(database, "get_db", get_db_with_trace)

    database.init_db()

    conn = sqlite3.connect(db_path)
    try:
        row_count = conn.execute("SELECT COUNT(*) FROM schema_versions").fetchone()[0]
        assert row_count == len(database.MIGRATIONS)
    finally:
        conn.close()

    joined = "\n".join(captured)
    assert "ALTER TABLE" not in joined
    assert "_new" not in joined


def test_dead_tables_absent_after_init(tmp_path, monkeypatch):
    db_path = tmp_path / "dead.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    database.init_db()

    conn = sqlite3.connect(db_path)
    try:
        table_names = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()

    assert "personal_info" not in table_names
    assert "job_descriptions" not in table_names
    assert "job_description_versions" not in table_names


def test_personal_info_data_migrates_to_users(tmp_path, monkeypatch):
    db_path = tmp_path / "personal.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE personal_info (
            id INTEGER PRIMARY KEY DEFAULT 1,
            full_name TEXT NOT NULL, email TEXT NOT NULL,
            phone TEXT, location TEXT, linkedin_url TEXT, summary TEXT,
            photo TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            CHECK (id = 1)
        );
        INSERT INTO personal_info (id, full_name, email, phone, location, linkedin_url, summary, photo)
            VALUES (1, 'Alice Example', 'alice@example.com', '555-0123', 'NYC', 'https://x', 'hi', 'photo.png');
    """)
    conn.commit()
    conn.close()

    database.init_db()

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT full_name, email, phone, location, linkedin_url, summary, photo FROM users WHERE id = 1"
        ).fetchone()
        assert row == ("Alice Example", "alice@example.com", "555-0123", "NYC", "https://x", "hi", "photo.png")

        table_names = {
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "personal_info" not in table_names
    finally:
        conn.close()


def test_legacy_job_description_versions_data_preserved(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy_jdv.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT NOT NULL, parsed_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO job_descriptions (id, raw_text) VALUES (1, 'jd one');
        CREATE TABLE job_description_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_description_id INTEGER NOT NULL,
            raw_text TEXT NOT NULL,
            version_number INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
        );
        INSERT INTO job_description_versions (id, job_description_id, raw_text, version_number)
            VALUES (1, 1, 'original text v1', 1),
                   (2, 1, 'edited text v2', 2);
    """)
    conn.commit()
    conn.close()

    database.init_db()

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, job_id, original_text, version_number FROM job_versions ORDER BY id"
        ).fetchall()
        assert rows == [(1, 1, "original text v1", 1), (2, 1, "edited text v2", 2)]

        table_names = {
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "job_description_versions" not in table_names
    finally:
        conn.close()


def test_personal_info_helper_tolerates_missing_photo(tmp_path, monkeypatch):
    db_path = tmp_path / "no_photo.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE personal_info (
            id INTEGER PRIMARY KEY DEFAULT 1,
            full_name TEXT NOT NULL, email TEXT NOT NULL,
            phone TEXT, location TEXT, linkedin_url TEXT, summary TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            CHECK (id = 1)
        );
        INSERT INTO personal_info (id, full_name, email, phone, location, linkedin_url, summary)
            VALUES (1, 'Bob NoPhoto', 'bob@example.com', '555-9999', 'LA', 'https://b', 'bio');
    """)
    conn.commit()
    conn.close()

    database.init_db()

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT full_name, email, phone, location, linkedin_url, summary, photo FROM users WHERE id = 1"
        ).fetchone()
        assert row[0] == "Bob NoPhoto"
        assert row[1] == "bob@example.com"
        assert row[6] is None
    finally:
        conn.close()


def test_recreate_drops_check_constraints(tmp_path, monkeypatch):
    db_path = tmp_path / "check.db"
    monkeypatch.setattr(database, "DATABASE", str(db_path))

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, original_text TEXT NOT NULL);
        INSERT INTO jobs (id, original_text) VALUES (1, 'job');
        CREATE TABLE generated_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            resume_content TEXT NOT NULL,
            language TEXT CHECK(language IN ('en', 'fr', 'nl')),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        );
    """)
    conn.commit()

    database._migrate_generated_resumes_fk_cascade(conn)

    table_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
    ).fetchone()[0]
    assert "CHECK" not in table_sql
    conn.close()


def test_live_app_db_upgrades_cleanly(tmp_path, monkeypatch):
    live_path = Path(__file__).resolve().parent.parent / "app.db"
    if not live_path.exists():
        pytest.skip("No app.db in project root")

    live_copy = tmp_path / "live_copy.db"
    shutil.copy(live_path, live_copy)

    monkeypatch.setattr(database, "DATABASE", str(live_copy))
    database.init_db()

    fresh = tmp_path / "fresh.db"
    monkeypatch.setattr(database, "DATABASE", str(fresh))
    database.init_db()

    equivalent, message = _check_schema_shape_equivalent(str(live_copy), str(fresh))
    assert equivalent, message

    conn = sqlite3.connect(live_copy)
    try:
        count = conn.execute("SELECT COUNT(*) FROM schema_versions").fetchone()[0]
        assert count == len(database.MIGRATIONS)
    finally:
        conn.close()
