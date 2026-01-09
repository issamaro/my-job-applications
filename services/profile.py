from database import get_db
from schemas import CompleteProfile


class ProfileService:
    def get_complete(self, user_id: int = 1) -> CompleteProfile:
        with get_db() as conn:
            personal_info = None
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                personal_info = dict(row)

            cursor = conn.execute(
                """
                SELECT * FROM work_experiences
                WHERE user_id = ?
                ORDER BY is_current DESC, start_date DESC
                """,
                (user_id,),
            )
            work_experiences = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute(
                "SELECT * FROM education WHERE user_id = ? ORDER BY graduation_year DESC",
                (user_id,),
            )
            education = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute(
                "SELECT * FROM skills WHERE user_id = ? ORDER BY name", (user_id,)
            )
            skills = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute(
                "SELECT * FROM projects WHERE user_id = ? ORDER BY start_date DESC",
                (user_id,),
            )
            projects = [dict(row) for row in cursor.fetchall()]

            cursor = conn.execute(
                "SELECT * FROM languages WHERE user_id = ? ORDER BY display_order ASC, id ASC",
                (user_id,),
            )
            languages = [dict(row) for row in cursor.fetchall()]

            return CompleteProfile(
                personal_info=personal_info,
                work_experiences=work_experiences,
                education=education,
                skills=skills,
                projects=projects,
                languages=languages,
            )

    def has_work_experience(self, user_id: int = 1) -> bool:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM work_experiences WHERE user_id = ?", (user_id,)
            )
            count = cursor.fetchone()[0]
            return count > 0


profile_service = ProfileService()
