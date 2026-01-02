from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import WorkExperience, WorkExperienceCreate, WorkExperienceUpdate

router = APIRouter(prefix="/api/work-experiences", tags=["work-experiences"])


@router.get("", response_model=list[WorkExperience])
async def list_work_experiences():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM work_experiences
            ORDER BY is_current DESC, start_date DESC
            """
        )
        rows = cursor.fetchall()
        return [WorkExperience.model_validate(dict(row)) for row in rows]


@router.post("", response_model=WorkExperience)
async def create_work_experience(exp: WorkExperienceCreate):
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO work_experiences (company, title, start_date, end_date, is_current, description, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
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
        conn.commit()
        exp_id = cursor.lastrowid

        cursor = conn.execute("SELECT * FROM work_experiences WHERE id = ?", (exp_id,))
        row = cursor.fetchone()
        return WorkExperience.model_validate(dict(row))


@router.get("/{exp_id}", response_model=WorkExperience)
async def get_work_experience(exp_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM work_experiences WHERE id = ?", (exp_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Work experience not found")
        return WorkExperience.model_validate(dict(row))


@router.put("/{exp_id}", response_model=WorkExperience)
async def update_work_experience(exp_id: int, exp: WorkExperienceUpdate):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM work_experiences WHERE id = ?", (exp_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Work experience not found")

        conn.execute(
            """
            UPDATE work_experiences SET
                company = ?,
                title = ?,
                start_date = ?,
                end_date = ?,
                is_current = ?,
                description = ?,
                location = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                exp.company,
                exp.title,
                exp.start_date,
                exp.end_date,
                1 if exp.is_current else 0,
                exp.description,
                exp.location,
                exp_id,
            ),
        )
        conn.commit()

        cursor = conn.execute("SELECT * FROM work_experiences WHERE id = ?", (exp_id,))
        row = cursor.fetchone()
        return WorkExperience.model_validate(dict(row))


@router.delete("/{exp_id}")
async def delete_work_experience(exp_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM work_experiences WHERE id = ?", (exp_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Work experience not found")

        conn.execute("DELETE FROM work_experiences WHERE id = ?", (exp_id,))
        conn.commit()
        return {"deleted": exp_id}
