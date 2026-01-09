import json
from datetime import datetime
from database import get_db


class JobService:
    def list_all(self) -> list[dict]:
        """Get all saved jobs with resume count, ordered by updated_at DESC"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT
                    j.id, j.title, j.company_name, j.original_text,
                    j.created_at, j.updated_at,
                    COUNT(gr.id) as resume_count
                FROM jobs j
                LEFT JOIN generated_resumes gr ON j.id = gr.job_id
                WHERE j.is_saved = 1
                GROUP BY j.id
                ORDER BY j.updated_at DESC
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    **dict(row),
                    "text_preview": dict(row)["original_text"][:200],
                }
                for row in rows
            ]

    def get(self, job_id: int) -> dict | None:
        """Get single job by ID"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT
                    j.id, j.title, j.company_name, j.original_text,
                    j.created_at, j.updated_at,
                    COUNT(gr.id) as resume_count
                FROM jobs j
                LEFT JOIN generated_resumes gr ON j.id = gr.job_id
                WHERE j.id = ?
                GROUP BY j.id
                """,
                (job_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def create(self, original_text: str) -> dict:
        """Save new job with default title"""
        now = datetime.now().isoformat()
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO jobs (original_text, title, updated_at, is_saved)
                VALUES (?, ?, ?, ?)
                """,
                (original_text, "Untitled Job", now, 1),
            )
            conn.commit()
            job_id = cursor.lastrowid
            return self.get(job_id)

    def update(self, job_id: int, data: dict) -> dict | None:
        """Update job title or text, create version if text changed"""
        current = self.get(job_id)
        if not current:
            return None

        with get_db() as conn:
            # If original_text changed, create version
            if data.get("original_text") and data["original_text"] != current["original_text"]:
                cursor = conn.execute(
                    "SELECT MAX(version_number) as max_version FROM job_versions WHERE job_id = ?",
                    (job_id,),
                )
                row = cursor.fetchone()
                max_version = row["max_version"] if row and row["max_version"] else 0

                conn.execute(
                    """
                    INSERT INTO job_versions (job_id, original_text, version_number)
                    VALUES (?, ?, ?)
                    """,
                    (job_id, current["original_text"], max_version + 1),
                )

            # Build update query
            updates = []
            params = []
            if data.get("title") is not None:
                updates.append("title = ?")
                params.append(data["title"])
            if data.get("original_text") is not None:
                updates.append("original_text = ?")
                params.append(data["original_text"])

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(job_id)

                conn.execute(
                    f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
                conn.commit()

            return self.get(job_id)

    def delete(self, job_id: int) -> bool:
        """Delete job - FK CASCADE handles generated_resumes and versions automatically"""
        with get_db() as conn:
            cursor = conn.execute(
                "DELETE FROM jobs WHERE id = ?",
                (job_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_resumes(self, job_id: int) -> list[dict]:
        """Get resumes linked to this job"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT id, job_title, company_name, match_score, created_at
                FROM generated_resumes
                WHERE job_id = ?
                ORDER BY created_at DESC
                """,
                (job_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_versions(self, job_id: int) -> list[dict]:
        """Get version history for job"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT id, version_number, original_text, created_at
                FROM job_versions
                WHERE job_id = ?
                ORDER BY version_number DESC
                """,
                (job_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def restore_version(self, job_id: int, version_id: int) -> dict | None:
        """Restore job text from version (creates new version first)"""
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT original_text FROM job_versions WHERE id = ? AND job_id = ?",
                (version_id, job_id),
            )
            version = cursor.fetchone()
            if not version:
                return None

            # Update with version text (this will create a new version via update())
            return self.update(job_id, {"original_text": version["original_text"]})


    def save_job_analysis(
        self,
        job_analysis: dict,
        title: str,
        company_name: str,
        original_text: str | None = None,
        job_id: int | None = None,
    ) -> int:
        """
        Single source of truth for saving job analysis (parsed_data) to a job.

        - If job_id is None: Creates new job with original_text, title, company_name, and parsed_data
        - If job_id is provided: Updates existing job's parsed_data (and title if still "Untitled Job")

        Returns the job id.
        """
        with get_db() as conn:
            parsed_data_json = json.dumps(job_analysis) if job_analysis else None

            if job_id is None:
                # INSERT: Create new job
                cursor = conn.execute(
                    """
                    INSERT INTO jobs (original_text, parsed_data, title, company_name, updated_at, is_saved)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
                    """,
                    (original_text, parsed_data_json, title, company_name),
                )
                conn.commit()
                return cursor.lastrowid
            else:
                # UPDATE: Check if existing job needs title update
                cursor = conn.execute(
                    "SELECT title FROM jobs WHERE id = ?",
                    (job_id,)
                )
                existing = cursor.fetchone()
                if not existing:
                    raise ValueError(f"Job with id {job_id} not found")

                if existing["title"] == "Untitled Job":
                    # Update title, company_name, and parsed_data
                    conn.execute(
                        """
                        UPDATE jobs
                        SET title = ?, company_name = ?, parsed_data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (title, company_name, parsed_data_json, job_id)
                    )
                else:
                    # Only update parsed_data and timestamp
                    conn.execute(
                        "UPDATE jobs SET parsed_data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (parsed_data_json, job_id)
                    )
                conn.commit()
                return job_id


job_service = JobService()
