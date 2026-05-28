# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: SQLite engine, session context manager, and schema migration runner.

import re
import sqlite3
from contextlib import contextmanager

from fastapi import HTTPException

DATABASE = "app.db"

VALID_TABLES = frozenset({
    "users", "work_experiences", "education", "skills",
    "projects", "languages", "jobs", "generated_resumes", "job_versions",
})


_INLINE_DDL = """
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
        user_id INTEGER DEFAULT 1,
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
        user_id INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        user_id INTEGER DEFAULT 1,
        UNIQUE(user_id, name)
    );

    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        technologies TEXT,
        url TEXT,
        start_date TEXT,
        end_date TEXT,
        user_id INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        level TEXT NOT NULL CHECK(level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
        display_order INTEGER NOT NULL DEFAULT 0,
        user_id INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_text TEXT NOT NULL,
        parsed_data TEXT,
        title TEXT DEFAULT 'Untitled Job',
        company_name TEXT,
        updated_at TEXT,
        is_saved INTEGER DEFAULT 1,
        user_id INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS job_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        original_text TEXT NOT NULL,
        version_number INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_job_versions_job_id ON job_versions(job_id);

    CREATE TABLE IF NOT EXISTS generated_resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        job_title TEXT,
        company_name TEXT,
        match_score REAL,
        resume_content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        jd_version_id INTEGER,
        language TEXT DEFAULT 'en',
        job_analysis TEXT,
        user_id INTEGER DEFAULT 1,
        prompt_path TEXT,
        prompt_hash TEXT,
        provider TEXT,
        model TEXT,
        profile_snapshot TEXT,
        raw_output TEXT,
        latency_ms INTEGER,
        input_tokens INTEGER,
        output_tokens INTEGER,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_generated_resumes_created
    ON generated_resumes(created_at DESC);
"""


MIGRATIONS: list[tuple[str, str]] = [
    ("20240601_jobs_title",                "ALTER TABLE jobs ADD COLUMN title TEXT DEFAULT 'Untitled Job'"),
    ("20240601_jobs_company_name",         "ALTER TABLE jobs ADD COLUMN company_name TEXT"),
    ("20240601_jobs_updated_at",           "ALTER TABLE jobs ADD COLUMN updated_at TEXT"),
    ("20240601_jobs_is_saved",             "ALTER TABLE jobs ADD COLUMN is_saved INTEGER DEFAULT 1"),
    ("20240601_jobs_user_id",              "ALTER TABLE jobs ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_resumes_jd_version_id",     "ALTER TABLE generated_resumes ADD COLUMN jd_version_id INTEGER"),
    ("20240601_resumes_language",          "ALTER TABLE generated_resumes ADD COLUMN language TEXT DEFAULT 'en'"),
    ("20240601_resumes_job_analysis",      "ALTER TABLE generated_resumes ADD COLUMN job_analysis TEXT"),
    ("20240601_resumes_user_id",           "ALTER TABLE generated_resumes ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_work_user_id",              "ALTER TABLE work_experiences ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_education_user_id",         "ALTER TABLE education ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_projects_user_id",          "ALTER TABLE projects ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_languages_user_id",         "ALTER TABLE languages ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20260527_breadcrumbs_prompt_path",   "ALTER TABLE generated_resumes ADD COLUMN prompt_path TEXT"),
    ("20260527_breadcrumbs_prompt_hash",   "ALTER TABLE generated_resumes ADD COLUMN prompt_hash TEXT"),
    ("20260527_breadcrumbs_provider",      "ALTER TABLE generated_resumes ADD COLUMN provider TEXT"),
    ("20260527_breadcrumbs_model",         "ALTER TABLE generated_resumes ADD COLUMN model TEXT"),
    ("20260527_breadcrumbs_profile_snap",  "ALTER TABLE generated_resumes ADD COLUMN profile_snapshot TEXT"),
    ("20260527_breadcrumbs_raw_output",    "ALTER TABLE generated_resumes ADD COLUMN raw_output TEXT"),
    ("20260527_breadcrumbs_latency_ms",    "ALTER TABLE generated_resumes ADD COLUMN latency_ms INTEGER"),
    ("20260527_breadcrumbs_input_tokens",  "ALTER TABLE generated_resumes ADD COLUMN input_tokens INTEGER"),
    ("20260527_breadcrumbs_output_tokens", "ALTER TABLE generated_resumes ADD COLUMN output_tokens INTEGER"),
]


_ADD_COLUMN_RE = re.compile(
    r"^\s*ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)\b",
    re.IGNORECASE,
)


def get_or_404(conn, table: str, id: int, entity_name: str, model_class=None):
    if table not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}")
    cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{entity_name} not found")
    if model_class:
        return model_class.model_validate(dict(row))
    return row


def exists_or_404(conn, table: str, id: int, entity_name: str):
    if table not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}")
    cursor = conn.execute(f"SELECT id FROM {table} WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail=f"{entity_name} not found")


def fetch_one(conn, table: str, id: int, model_class):
    if table not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}")
    cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
    return model_class.model_validate(dict(cursor.fetchone()))


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _migrate_recreate_with_constraint(conn, source_table, rename_map, additions, constraint_clause):
    pragma_rows = conn.execute(f"PRAGMA table_info({source_table})").fetchall()
    master_row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (source_table,),
    ).fetchone()
    source_sql = master_row[0] if master_row else ""

    has_autoincrement = bool(re.search(
        r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b",
        source_sql,
        re.IGNORECASE,
    ))
    id_declaration = "id INTEGER PRIMARY KEY AUTOINCREMENT" if has_autoincrement else "id INTEGER PRIMARY KEY"

    non_primary_rows = [row for row in pragma_rows if row[5] == 0]
    non_primary_pairs = []
    non_primary_declarations = []
    for _cid, name, type_, notnull, default_value, _primary_key_flag in non_primary_rows:
        destination_name = rename_map.get(name, name)
        declaration = f"{destination_name} {type_}"
        if notnull:
            declaration += " NOT NULL"
        if default_value is not None:
            declaration += f" DEFAULT {default_value}"
        non_primary_declarations.append(declaration)
        non_primary_pairs.append((name, destination_name))

    addition_declarations = [declaration for declaration, _ in additions]
    addition_selects = [select for _, select in additions]
    addition_names = [declaration.split()[0] for declaration in addition_declarations]

    new_table = f"{source_table}_new"
    create_sql = (
        f"CREATE TABLE {new_table} ("
        + ", ".join([id_declaration, *non_primary_declarations, *addition_declarations, constraint_clause])
        + ")"
    )

    destination_columns_in_order = ["id", *(destination for _, destination in non_primary_pairs), *addition_names]
    source_expressions_in_order = ["id", *(source for source, _ in non_primary_pairs), *addition_selects]

    index_snapshots = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL",
        (source_table,),
    ).fetchall()

    conn.execute(create_sql)
    conn.execute(
        f"INSERT INTO {new_table} ({', '.join(destination_columns_in_order)}) "
        f"SELECT {', '.join(source_expressions_in_order)} FROM {source_table}"
    )
    conn.execute(f"DROP TABLE {source_table}")
    conn.execute(f"ALTER TABLE {new_table} RENAME TO {source_table}")

    for (index_sql,) in index_snapshots:
        conn.execute(index_sql)

    conn.commit()


def _migrate_skills_unique_constraint(conn):
    cursor = conn.execute("PRAGMA table_info(skills)")
    columns = [row[1] for row in cursor.fetchall()]
    if "user_id" in columns:
        return
    _migrate_recreate_with_constraint(
        conn,
        source_table="skills",
        rename_map={},
        additions=[("user_id INTEGER DEFAULT 1", "1")],
        constraint_clause="UNIQUE(user_id, name)",
    )


def _migrate_job_descriptions_to_jobs(conn):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='job_descriptions'"
    )
    has_old_table = cursor.fetchone() is not None

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
    )
    has_new_table = cursor.fetchone() is not None

    if has_old_table and not has_new_table:
        conn.execute("ALTER TABLE job_descriptions RENAME TO jobs")
        conn.commit()
    elif has_old_table and has_new_table:
        cursor = conn.execute("SELECT COUNT(*) FROM jobs")
        new_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM job_descriptions")
        old_count = cursor.fetchone()[0]

        if new_count == 0 and old_count > 0:
            conn.execute("DROP TABLE jobs")
            conn.execute("ALTER TABLE job_descriptions RENAME TO jobs")
            conn.commit()
        elif old_count == 0:
            conn.execute("DROP TABLE job_descriptions")
            conn.commit()


def _migrate_raw_text_to_original_text(conn):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
    )
    if not cursor.fetchone():
        return

    cursor = conn.execute("PRAGMA table_info(jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "raw_text" in columns and "original_text" not in columns:
        conn.execute("ALTER TABLE jobs RENAME COLUMN raw_text TO original_text")
        conn.commit()


def _migrate_job_description_versions_to_job_versions(conn):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='job_description_versions'"
    )
    has_old_table = cursor.fetchone() is not None

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='job_versions'"
    )
    has_new_table = cursor.fetchone() is not None

    if has_old_table and not has_new_table:
        conn.execute("ALTER TABLE job_description_versions RENAME TO job_versions")
        conn.execute("ALTER TABLE job_versions RENAME COLUMN job_description_id TO job_id")
        conn.execute("ALTER TABLE job_versions RENAME COLUMN raw_text TO original_text")
        conn.commit()
    elif has_old_table and has_new_table:
        new_count = conn.execute("SELECT COUNT(*) FROM job_versions").fetchone()[0]
        old_count = conn.execute("SELECT COUNT(*) FROM job_description_versions").fetchone()[0]
        if new_count == 0 and old_count > 0:
            conn.execute("DROP TABLE job_versions")
            conn.execute("ALTER TABLE job_description_versions RENAME TO job_versions")
            conn.execute("ALTER TABLE job_versions RENAME COLUMN job_description_id TO job_id")
            conn.execute("ALTER TABLE job_versions RENAME COLUMN raw_text TO original_text")
            conn.commit()
        elif old_count == 0:
            conn.execute("DROP TABLE job_description_versions")
            conn.commit()

    conn.execute("DROP INDEX IF EXISTS idx_job_description_versions_jd_id")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_job_versions_job_id ON job_versions(job_id)")
    conn.commit()


def _migrate_personal_info_to_users(conn):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='personal_info'"
    )
    if cursor.fetchone() is None:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM users WHERE id = 1")
    if cursor.fetchone()[0] != 0:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM personal_info WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        return
    target_columns = ("email", "full_name", "phone", "location", "linkedin_url",
                      "summary", "photo", "updated_at")
    source_columns = {row[1] for row in conn.execute("PRAGMA table_info(personal_info)").fetchall()}
    cols_present = [c for c in target_columns if c in source_columns]
    col_list = ", ".join(cols_present)
    conn.execute(
        f"INSERT INTO users (id, {col_list}) SELECT 1, {col_list} FROM personal_info WHERE id = 1"
    )
    conn.commit()


def _migrate_generated_resumes_fk_cascade(conn):
    cursor = conn.execute("PRAGMA table_info(generated_resumes)")
    columns = [row[1] for row in cursor.fetchall()]
    has_job_id = "job_id" in columns
    has_job_description_id = "job_description_id" in columns

    cursor = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
    )
    row = cursor.fetchone()
    if row and "ON DELETE CASCADE" in (row[0] or "") and has_job_id and not has_job_description_id:
        return

    rename_map = {} if has_job_id else {"job_description_id": "job_id"}
    _migrate_recreate_with_constraint(
        conn,
        source_table="generated_resumes",
        rename_map=rename_map,
        additions=[],
        constraint_clause="FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE",
    )


def _migrate_apply_pending(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_versions ("
        "version TEXT PRIMARY KEY, "
        "applied_at TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    applied = {row[0] for row in conn.execute(
        "SELECT version FROM schema_versions"
    ).fetchall()}
    for version_id, sql in MIGRATIONS:
        if version_id in applied:
            continue
        match = _ADD_COLUMN_RE.match(sql)
        if match:
            table, column = match.group(1), match.group(2)
            existing = {row[1] for row in conn.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()}
            if column in existing:
                conn.execute(
                    "INSERT INTO schema_versions (version) VALUES (?)",
                    (version_id,),
                )
                conn.commit()
                continue
        try:
            conn.execute(sql)
        except Exception as e:
            raise type(e)(f"[{version_id}] {e}") from e
        conn.execute(
            "INSERT INTO schema_versions (version) VALUES (?)",
            (version_id,),
        )
        conn.commit()


def init_db():
    with get_db() as conn:
        conn.executescript(_INLINE_DDL)
        _migrate_job_descriptions_to_jobs(conn)
        _migrate_raw_text_to_original_text(conn)
        _migrate_job_description_versions_to_job_versions(conn)
        _migrate_personal_info_to_users(conn)
        _migrate_skills_unique_constraint(conn)
        _migrate_generated_resumes_fk_cascade(conn)
        _migrate_apply_pending(conn)
        conn.execute(
            "UPDATE jobs SET updated_at = created_at WHERE updated_at IS NULL"
        )
        conn.execute(
            "UPDATE generated_resumes "
            "SET job_analysis = (SELECT parsed_data FROM jobs WHERE jobs.id = generated_resumes.job_id) "
            "WHERE job_analysis IS NULL"
        )
        conn.execute("DROP TABLE IF EXISTS personal_info")
        conn.commit()
