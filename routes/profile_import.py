from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import ProfileImport, ProfileImportResponse

router = APIRouter(prefix="/api/profile", tags=["profile-import"])


@router.put("/import", response_model=ProfileImportResponse)
async def import_profile(profile: ProfileImport):
    """Import complete profile from JSON, replacing all existing data except photo."""
    try:
        with get_db() as conn:
            # 1. Clear existing data for user_id=1 (except photo)
            conn.execute("DELETE FROM work_experiences WHERE user_id = 1")
            conn.execute("DELETE FROM education WHERE user_id = 1")
            conn.execute("DELETE FROM skills WHERE user_id = 1")
            conn.execute("DELETE FROM projects WHERE user_id = 1")
            conn.execute("DELETE FROM languages WHERE user_id = 1")

            # 2. Update or insert user (preserve photo column)
            cursor = conn.execute("SELECT id, photo FROM users WHERE id = 1")
            row = cursor.fetchone()

            if row:
                conn.execute(
                    """
                    UPDATE users SET
                        full_name = ?,
                        email = ?,
                        phone = ?,
                        location = ?,
                        linkedin_url = ?,
                        summary = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                    """,
                    (
                        profile.personal_info.full_name,
                        profile.personal_info.email,
                        profile.personal_info.phone,
                        profile.personal_info.location,
                        profile.personal_info.linkedin_url,
                        profile.personal_info.summary,
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO users (id, full_name, email, phone, location, linkedin_url, summary)
                    VALUES (1, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        profile.personal_info.full_name,
                        profile.personal_info.email,
                        profile.personal_info.phone,
                        profile.personal_info.location,
                        profile.personal_info.linkedin_url,
                        profile.personal_info.summary,
                    ),
                )

            # 3. Insert work experiences
            for exp in profile.work_experiences:
                conn.execute(
                    """
                    INSERT INTO work_experiences (company, title, start_date, end_date, is_current, description, location, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        exp.company,
                        exp.title,
                        exp.start_date,
                        exp.end_date,
                        1 if exp.is_current else 0,
                        exp.description,
                        exp.location,
                    ),
                )

            # 4. Insert education
            for edu in profile.education:
                conn.execute(
                    """
                    INSERT INTO education (institution, degree, field_of_study, graduation_year, gpa, notes, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        edu.institution,
                        edu.degree,
                        edu.field_of_study,
                        edu.graduation_year,
                        edu.gpa,
                        edu.notes,
                    ),
                )

            # 5. Insert skills
            for skill in profile.skills:
                try:
                    conn.execute(
                        "INSERT INTO skills (name, user_id) VALUES (?, 1)",
                        (skill.name,),
                    )
                except Exception:
                    # Skill might already exist (UNIQUE constraint)
                    pass

            # 6. Insert projects
            for project in profile.projects:
                conn.execute(
                    """
                    INSERT INTO projects (name, description, technologies, url, start_date, end_date, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        project.name,
                        project.description,
                        project.technologies,
                        project.url,
                        project.start_date,
                        project.end_date,
                    ),
                )

            # 7. Insert languages
            for idx, lang in enumerate(profile.languages):
                conn.execute(
                    """
                    INSERT INTO languages (name, level, display_order, user_id)
                    VALUES (?, ?, ?, 1)
                    """,
                    (lang.name, lang.level.value, idx),
                )

            # 8. Commit (all or nothing)
            conn.commit()

            return ProfileImportResponse(
                message="Profile imported successfully",
                counts={
                    "work_experiences": len(profile.work_experiences),
                    "education": len(profile.education),
                    "skills": len(profile.skills),
                    "projects": len(profile.projects),
                    "languages": len(profile.languages),
                },
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Import failed. Please try again.")
