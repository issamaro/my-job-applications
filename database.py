import sqlite3
from contextlib import contextmanager

from fastapi import HTTPException

DATABASE = "app.db"


def get_or_404(conn, table: str, id: int, entity_name: str, model_class=None):
    """Fetch a row by ID or raise 404. Optionally return as Pydantic model."""
    cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{entity_name} not found")
    if model_class:
        return model_class.model_validate(dict(row))
    return row


def exists_or_404(conn, table: str, id: int, entity_name: str):
    """Check existence or raise 404 (for UPDATE/DELETE)."""
    cursor = conn.execute(f"SELECT id FROM {table} WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail=f"{entity_name} not found")


def fetch_one(conn, table: str, id: int, model_class):
    """Fetch a row by ID and return as Pydantic model (use after INSERT/UPDATE)."""
    cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
    return model_class.model_validate(dict(cursor.fetchone()))


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable FK cascade
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS personal_info (
                id INTEGER PRIMARY KEY DEFAULT 1,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                location TEXT,
                linkedin_url TEXT,
                summary TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CHECK (id = 1)
            );

            CREATE TABLE IF NOT EXISTS work_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                is_current INTEGER DEFAULT 0,
                description TEXT,
                location TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                institution TEXT NOT NULL,
                degree TEXT NOT NULL,
                field_of_study TEXT,
                graduation_year INTEGER,
                gpa REAL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                technologies TEXT,
                url TEXT,
                start_date TEXT,
                end_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS languages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level TEXT NOT NULL CHECK(level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
                display_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT NOT NULL,
                parsed_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS generated_resumes (
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

            CREATE INDEX IF NOT EXISTS idx_generated_resumes_created
            ON generated_resumes(created_at DESC);
        """)

        # Migrations for Saved Job Descriptions feature
        # Add new columns to job_descriptions (idempotent with try/except)
        migrations = [
            "ALTER TABLE job_descriptions ADD COLUMN title TEXT DEFAULT 'Untitled Job'",
            "ALTER TABLE job_descriptions ADD COLUMN company_name TEXT",
            "ALTER TABLE job_descriptions ADD COLUMN updated_at TEXT",
            "ALTER TABLE job_descriptions ADD COLUMN is_saved INTEGER DEFAULT 1",
            "ALTER TABLE generated_resumes ADD COLUMN jd_version_id INTEGER",
            # Photo Management feature
            "ALTER TABLE personal_info ADD COLUMN photo TEXT",
            # Multi-Language Resume Generation feature
            "ALTER TABLE generated_resumes ADD COLUMN language TEXT DEFAULT 'en'",
        ]
        for sql in migrations:
            try:
                conn.execute(sql)
            except sqlite3.OperationalError:
                pass  # Column already exists

        # Backfill updated_at from created_at
        conn.execute("""
            UPDATE job_descriptions SET updated_at = created_at WHERE updated_at IS NULL
        """)

        # Create version history table with FK CASCADE
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS job_description_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_description_id INTEGER NOT NULL,
                raw_text TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_job_description_versions_jd_id
            ON job_description_versions(job_description_id);
        """)
