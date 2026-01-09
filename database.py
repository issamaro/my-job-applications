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


def _migrate_skills_unique_constraint(conn):
    """Recreate skills table with UNIQUE(user_id, name) constraint.

    SQLite doesn't support ALTER TABLE for constraint changes.
    This migration recreates the table with correct unique constraint.
    """
    # Check if migration already done (table has user_id column)
    cursor = conn.execute("PRAGMA table_info(skills)")
    columns = [row[1] for row in cursor.fetchall()]
    if "user_id" in columns:
        return  # Already migrated

    # Step 1: Create new table with constraint
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER DEFAULT 1,
            UNIQUE(user_id, name)
        )
    """)

    # Step 2: Copy data (only if new table is empty)
    cursor = conn.execute("SELECT COUNT(*) FROM skills_new")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            INSERT INTO skills_new (id, name, user_id)
            SELECT id, name, 1 FROM skills
        """)

    # Step 3: Drop old table
    conn.execute("DROP TABLE IF EXISTS skills")

    # Step 4: Rename new to old
    conn.execute("ALTER TABLE skills_new RENAME TO skills")

    conn.commit()


def _migrate_job_descriptions_to_jobs(conn):
    """Rename job_descriptions table to jobs.

    Uses SQLite ALTER TABLE RENAME for fast, index-preserving rename.
    Handles partially migrated state where both tables may exist.
    """
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='job_descriptions'"
    )
    has_old_table = cursor.fetchone() is not None

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
    )
    has_new_table = cursor.fetchone() is not None

    if has_old_table and not has_new_table:
        # Normal case: rename old to new
        conn.execute("ALTER TABLE job_descriptions RENAME TO jobs")
        conn.commit()
    elif has_old_table and has_new_table:
        # Partially migrated: both exist
        cursor = conn.execute("SELECT COUNT(*) FROM jobs")
        new_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM job_descriptions")
        old_count = cursor.fetchone()[0]

        if new_count == 0 and old_count > 0:
            # New table is empty, old has data - drop new and rename old
            conn.execute("DROP TABLE jobs")
            conn.execute("ALTER TABLE job_descriptions RENAME TO jobs")
            conn.commit()
        elif old_count == 0:
            # Old table is empty - just drop it
            conn.execute("DROP TABLE job_descriptions")
            conn.commit()
        # else: both have data - keep new table (assume it's more current)


def _migrate_raw_text_to_original_text(conn):
    """Rename raw_text column to original_text in jobs table.

    SQLite 3.25+ supports ALTER TABLE RENAME COLUMN.
    """
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
    )
    if not cursor.fetchone():
        return  # Table doesn't exist yet

    cursor = conn.execute("PRAGMA table_info(jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "raw_text" in columns and "original_text" not in columns:
        conn.execute("ALTER TABLE jobs RENAME COLUMN raw_text TO original_text")
        conn.commit()


def _migrate_job_description_versions_to_job_versions(conn):
    """Rename job_description_versions table to job_versions.

    Also renames column job_description_id to job_id and raw_text to original_text.
    """
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='job_description_versions'"
    )
    has_old_table = cursor.fetchone() is not None

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='job_versions'"
    )
    has_new_table = cursor.fetchone() is not None

    if has_old_table and not has_new_table:
        # Rename table and columns
        conn.execute("ALTER TABLE job_description_versions RENAME TO job_versions")
        conn.execute("ALTER TABLE job_versions RENAME COLUMN job_description_id TO job_id")
        conn.execute("ALTER TABLE job_versions RENAME COLUMN raw_text TO original_text")
        conn.commit()
    elif has_old_table and has_new_table:
        # Both exist - check if old is empty
        cursor = conn.execute("SELECT COUNT(*) FROM job_description_versions")
        old_count = cursor.fetchone()[0]
        if old_count == 0:
            conn.execute("DROP TABLE job_description_versions")
            conn.commit()


def _migrate_generated_resumes_fk_cascade(conn):
    """Recreate generated_resumes table with FK CASCADE constraint.

    SQLite doesn't support ALTER TABLE for FK modification.
    This migration recreates the table with correct ON DELETE CASCADE.
    Also renames job_description_id column to job_id.
    """
    cursor = conn.execute("PRAGMA table_info(generated_resumes)")
    columns = [row[1] for row in cursor.fetchall()]
    has_job_id = "job_id" in columns
    has_job_description_id = "job_description_id" in columns

    # Check if migration already done (has CASCADE and correct column name)
    cursor = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
    )
    row = cursor.fetchone()
    if row and "ON DELETE CASCADE" in (row[0] or "") and has_job_id and not has_job_description_id:
        return  # Already fully migrated

    # Determine source column name
    source_column = "job_id" if has_job_id else "job_description_id"

    # Step 1: Create new table with correct FK and column name
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generated_resumes_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            job_title TEXT,
            company_name TEXT,
            match_score REAL,
            resume_content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            jd_version_id INTEGER,
            language TEXT DEFAULT 'en',
            job_analysis TEXT,
            user_id INTEGER DEFAULT 1,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
        )
    """)

    # Step 2: Copy data (only if new table is empty)
    cursor = conn.execute("SELECT COUNT(*) FROM generated_resumes_new")
    if cursor.fetchone()[0] == 0:
        conn.execute(f"""
            INSERT INTO generated_resumes_new
            (id, job_id, job_title, company_name, match_score,
             resume_content, created_at, updated_at, jd_version_id, language,
             job_analysis, user_id)
            SELECT id, {source_column}, job_title, company_name, match_score,
                   resume_content, created_at, updated_at, jd_version_id, language,
                   job_analysis, user_id
            FROM generated_resumes
        """)

    # Step 3: Drop old table
    conn.execute("DROP TABLE IF EXISTS generated_resumes")

    # Step 4: Rename new to old
    conn.execute("ALTER TABLE generated_resumes_new RENAME TO generated_resumes")

    # Step 5: Recreate index
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_generated_resumes_created
        ON generated_resumes(created_at DESC)
    """)

    conn.commit()


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

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                location TEXT,
                linkedin_url TEXT,
                summary TEXT,
                photo TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
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
            # Job Application Domain Redesign: job_analysis per resume + multi-user prep
            "ALTER TABLE generated_resumes ADD COLUMN job_analysis TEXT",
            "ALTER TABLE job_descriptions ADD COLUMN user_id INTEGER DEFAULT 1",
            "ALTER TABLE generated_resumes ADD COLUMN user_id INTEGER DEFAULT 1",
            # User/Profile Domain Redesign: add user_id to profile tables
            "ALTER TABLE work_experiences ADD COLUMN user_id INTEGER DEFAULT 1",
            "ALTER TABLE education ADD COLUMN user_id INTEGER DEFAULT 1",
            "ALTER TABLE projects ADD COLUMN user_id INTEGER DEFAULT 1",
            "ALTER TABLE languages ADD COLUMN user_id INTEGER DEFAULT 1",
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

        # Job Application Domain Redesign: Table and column renames
        # MUST run BEFORE any queries that reference new names
        _migrate_job_descriptions_to_jobs(conn)
        _migrate_raw_text_to_original_text(conn)
        _migrate_job_description_versions_to_job_versions(conn)

        # Create job_versions table with NEW schema (for fresh installs or after migration)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS job_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                original_text TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_job_versions_job_id
            ON job_versions(job_id);
        """)

        # Job Application Domain Redesign: Backfill job_analysis from jobs parsed_data
        # Check which column exists for the JOIN
        cursor = conn.execute("PRAGMA table_info(generated_resumes)")
        gr_columns = [row[1] for row in cursor.fetchall()]
        job_fk_col = "job_id" if "job_id" in gr_columns else "job_description_id"

        conn.execute(f"""
            UPDATE generated_resumes
            SET job_analysis = (
                SELECT parsed_data FROM jobs
                WHERE jobs.id = generated_resumes.{job_fk_col}
            )
            WHERE job_analysis IS NULL
        """)

        # Job Application Domain Redesign: Table recreation for FK CASCADE
        # SQLite doesn't support ALTER TABLE for FK modification, must recreate table
        _migrate_generated_resumes_fk_cascade(conn)

        # User/Profile Domain Redesign: Migrate personal_info data to users table
        # Check if personal_info table exists first
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='personal_info'"
        )
        has_personal_info = cursor.fetchone() is not None

        if has_personal_info:
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE id = 1")
            if cursor.fetchone()[0] == 0:
                # Check if personal_info has data to migrate
                cursor = conn.execute("SELECT COUNT(*) FROM personal_info WHERE id = 1")
                if cursor.fetchone()[0] > 0:
                    conn.execute("""
                        INSERT INTO users (id, email, full_name, phone, location, linkedin_url, summary, photo, updated_at)
                        SELECT 1, email, full_name, phone, location, linkedin_url, summary, photo, updated_at
                        FROM personal_info WHERE id = 1
                    """)
                    conn.commit()

        # User/Profile Domain Redesign: Recreate skills with UNIQUE(user_id, name) constraint
        _migrate_skills_unique_constraint(conn)

        # User/Profile Domain Redesign: Drop personal_info table (data migrated to users)
        conn.execute("DROP TABLE IF EXISTS personal_info")
        conn.commit()
