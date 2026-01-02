from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import Education, EducationCreate, EducationUpdate

router = APIRouter(prefix="/api/education", tags=["education"])


@router.get("", response_model=list[Education])
async def list_education():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM education
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
            INSERT INTO education (institution, degree, field_of_study, graduation_year, gpa, notes)
            VALUES (?, ?, ?, ?, ?, ?)
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
        edu_id = cursor.lastrowid

        cursor = conn.execute("SELECT * FROM education WHERE id = ?", (edu_id,))
        row = cursor.fetchone()
        return Education.model_validate(dict(row))


@router.get("/{edu_id}", response_model=Education)
async def get_education(edu_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM education WHERE id = ?", (edu_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Education not found")
        return Education.model_validate(dict(row))


@router.put("/{edu_id}", response_model=Education)
async def update_education(edu_id: int, edu: EducationUpdate):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM education WHERE id = ?", (edu_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Education not found")

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

        cursor = conn.execute("SELECT * FROM education WHERE id = ?", (edu_id,))
        row = cursor.fetchone()
        return Education.model_validate(dict(row))


@router.delete("/{edu_id}")
async def delete_education(edu_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM education WHERE id = ?", (edu_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Education not found")

        conn.execute("DELETE FROM education WHERE id = ?", (edu_id,))
        conn.commit()
        return {"deleted": edu_id}
