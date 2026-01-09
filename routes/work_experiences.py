from fastapi import APIRouter
from database import get_db, get_or_404, exists_or_404, fetch_one
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
        return fetch_one(conn, "work_experiences", cursor.lastrowid, WorkExperience)


@router.get("/{exp_id}", response_model=WorkExperience)
async def get_work_experience(exp_id: int):
    with get_db() as conn:
        return get_or_404(conn, "work_experiences", exp_id, "Work experience", WorkExperience)


@router.put("/{exp_id}", response_model=WorkExperience)
async def update_work_experience(exp_id: int, exp: WorkExperienceUpdate):
    with get_db() as conn:
        exists_or_404(conn, "work_experiences", exp_id, "Work experience")

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
        return fetch_one(conn, "work_experiences", exp_id, WorkExperience)


@router.delete("/{exp_id}")
async def delete_work_experience(exp_id: int):
    with get_db() as conn:
        exists_or_404(conn, "work_experiences", exp_id, "Work experience")
        conn.execute("DELETE FROM work_experiences WHERE id = ?", (exp_id,))
        conn.commit()
        return {"deleted": exp_id}
