from fastapi import APIRouter
from database import get_db, get_or_404, exists_or_404, fetch_one
from schemas import Education, EducationCreate, EducationUpdate

router = APIRouter(prefix="/api/education", tags=["education"])


@router.get("", response_model=list[Education])
async def list_education():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM education
            WHERE user_id = 1
            ORDER BY graduation_year DESC
            """
        )
        rows = cursor.fetchall()
        return [Education.model_validate(dict(row)) for row in rows]


@router.post("", response_model=Education)
async def create_education(edu: EducationCreate):
    with get_db() as conn:
        cursor = conn.execute(
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
        conn.commit()
        return fetch_one(conn, "education", cursor.lastrowid, Education)


@router.get("/{edu_id}", response_model=Education)
async def get_education(edu_id: int):
    with get_db() as conn:
        return get_or_404(conn, "education", edu_id, "Education", Education)


@router.put("/{edu_id}", response_model=Education)
async def update_education(edu_id: int, edu: EducationUpdate):
    with get_db() as conn:
        exists_or_404(conn, "education", edu_id, "Education")

        conn.execute(
            """
            UPDATE education SET
                institution = ?,
                degree = ?,
                field_of_study = ?,
                graduation_year = ?,
                gpa = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                edu.institution,
                edu.degree,
                edu.field_of_study,
                edu.graduation_year,
                edu.gpa,
                edu.notes,
                edu_id,
            ),
        )
        conn.commit()
        return fetch_one(conn, "education", edu_id, Education)


@router.delete("/{edu_id}")
async def delete_education(edu_id: int):
    with get_db() as conn:
        exists_or_404(conn, "education", edu_id, "Education")
        conn.execute("DELETE FROM education WHERE id = ?", (edu_id,))
        conn.commit()
        return {"deleted": edu_id}
