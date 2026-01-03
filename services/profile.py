from database import get_db
from schemas import CompleteProfile


class ProfileService:
    def get_complete(self) -> CompleteProfile:
        with get_db() as conn:
            personal_info = None
            cursor = conn.execute("SELECT * FROM personal_info WHERE id = 1")
            row = cursor.fetchone()
            if row:
                personal_info = dict(row)

            cursor = conn.execute(
                """
                SELECT * FROM work_experiences
                ORDER BY is_current DESC, start_date DESC
                """
            )
            work_experiences = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute("SELECT * FROM education ORDER BY graduation_year DESC")
            education = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute("SELECT * FROM skills ORDER BY name")
            skills = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute("SELECT * FROM projects ORDER BY start_date DESC")
            projects = [dict(row) for row in cursor.fetchall()]

            return CompleteProfile(
                personal_info=personal_info,
                work_experiences=work_experiences,
                education=education,
                skills=skills,
                projects=projects,
            )

    def has_work_experience(self) -> bool:
        with get_db() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM work_experiences")
            count = cursor.fetchone()[0]
            return count > 0


profile_service = ProfileService()
