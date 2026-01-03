from datetime import datetime
from database import get_db


class JobDescriptionService:
    def list_all(self) -> list[dict]:
        """Get all saved JDs with resume count, ordered by updated_at DESC"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT
                    jd.id, jd.title, jd.company_name, jd.raw_text,
                    jd.created_at, jd.updated_at,
                    COUNT(gr.id) as resume_count
                FROM job_descriptions jd
                LEFT JOIN generated_resumes gr ON jd.id = gr.job_description_id
                WHERE jd.is_saved = 1
                GROUP BY jd.id
                ORDER BY jd.updated_at DESC
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    **dict(row),
                    "raw_text_preview": dict(row)["raw_text"][:200],
                }
                for row in rows
            ]

    def get(self, jd_id: int) -> dict | None:
        """Get single JD by ID"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT
                    jd.id, jd.title, jd.company_name, jd.raw_text,
                    jd.created_at, jd.updated_at,
                    COUNT(gr.id) as resume_count
                FROM job_descriptions jd
                LEFT JOIN generated_resumes gr ON jd.id = gr.job_description_id
                WHERE jd.id = ?
                GROUP BY jd.id
                """,
                (jd_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def create(self, raw_text: str) -> dict:
        """Save new JD with default title"""
        now = datetime.now().isoformat()
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO job_descriptions (raw_text, title, updated_at, is_saved)
                VALUES (?, ?, ?, ?)
                """,
                (raw_text, "Untitled Job", now, 1),
            )
            conn.commit()
            jd_id = cursor.lastrowid
            return self.get(jd_id)

    def update(self, jd_id: int, data: dict) -> dict | None:
        """Update JD title or text, create version if text changed"""
        current = self.get(jd_id)
        if not current:
            return None

        with get_db() as conn:
            # If raw_text changed, create version
            if data.get("raw_text") and data["raw_text"] != current["raw_text"]:
                cursor = conn.execute(
                    "SELECT MAX(version_number) as max_version FROM job_description_versions WHERE job_description_id = ?",
                    (jd_id,),
                )
                row = cursor.fetchone()
                max_version = row["max_version"] if row and row["max_version"] else 0

                conn.execute(
                    """
                    INSERT INTO job_description_versions (job_description_id, raw_text, version_number)
                    VALUES (?, ?, ?)
                    """,
                    (jd_id, current["raw_text"], max_version + 1),
                )

            # Build update query
            updates = []
            params = []
            if data.get("title") is not None:
                updates.append("title = ?")
                params.append(data["title"])
            if data.get("raw_text") is not None:
                updates.append("raw_text = ?")
                params.append(data["raw_text"])

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(jd_id)

                conn.execute(
                    f"UPDATE job_descriptions SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
                conn.commit()

            return self.get(jd_id)

    def delete(self, jd_id: int) -> bool:
        """Delete JD and cascade to resumes + versions"""
        with get_db() as conn:
            # Manual delete for legacy FK without CASCADE
            conn.execute(
                "DELETE FROM generated_resumes WHERE job_description_id = ?",
                (jd_id,),
            )
            # job_description_versions has CASCADE, auto-deletes
            cursor = conn.execute(
                "DELETE FROM job_descriptions WHERE id = ?",
                (jd_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_resumes(self, jd_id: int) -> list[dict]:
        """Get resumes linked to this JD"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT id, job_title, company_name, match_score, created_at
                FROM generated_resumes
                WHERE job_description_id = ?
                ORDER BY created_at DESC
                """,
                (jd_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_versions(self, jd_id: int) -> list[dict]:
        """Get version history for JD"""
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT id, version_number, raw_text, created_at
                FROM job_description_versions
                WHERE job_description_id = ?
                ORDER BY version_number DESC
                """,
                (jd_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def restore_version(self, jd_id: int, version_id: int) -> dict | None:
        """Restore JD text from version (creates new version first)"""
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT raw_text FROM job_description_versions WHERE id = ? AND job_description_id = ?",
                (version_id, jd_id),
            )
            version = cursor.fetchone()
            if not version:
                return None

            # Update with version text (this will create a new version via update())
            return self.update(jd_id, {"raw_text": version["raw_text"]})


job_description_service = JobDescriptionService()
