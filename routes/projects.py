from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import Project, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[Project])
async def list_projects():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM projects
            ORDER BY created_at DESC
            """
        )
        rows = cursor.fetchall()
        return [Project.model_validate(dict(row)) for row in rows]


@router.post("", response_model=Project)
async def create_project(proj: ProjectCreate):
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO projects (name, description, technologies, url, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                proj.name,
                proj.description,
                proj.technologies,
                proj.url,
                proj.start_date,
                proj.end_date,
            ),
        )
        conn.commit()
        proj_id = cursor.lastrowid

        cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (proj_id,))
        row = cursor.fetchone()
        return Project.model_validate(dict(row))


@router.get("/{proj_id}", response_model=Project)
async def get_project(proj_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (proj_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return Project.model_validate(dict(row))


@router.put("/{proj_id}", response_model=Project)
async def update_project(proj_id: int, proj: ProjectUpdate):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM projects WHERE id = ?", (proj_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Project not found")

        conn.execute(
            """
            UPDATE projects SET
                name = ?,
                description = ?,
                technologies = ?,
                url = ?,
                start_date = ?,
                end_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                proj.name,
                proj.description,
                proj.technologies,
                proj.url,
                proj.start_date,
                proj.end_date,
                proj_id,
            ),
        )
        conn.commit()

        cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (proj_id,))
        row = cursor.fetchone()
        return Project.model_validate(dict(row))


@router.delete("/{proj_id}")
async def delete_project(proj_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM projects WHERE id = ?", (proj_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Project not found")

        conn.execute("DELETE FROM projects WHERE id = ?", (proj_id,))
        conn.commit()
        return {"deleted": proj_id}
