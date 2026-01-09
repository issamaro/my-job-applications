from fastapi import APIRouter
from database import get_db, get_or_404, exists_or_404, fetch_one
from schemas import Project, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[Project])
async def list_projects():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM projects
            WHERE user_id = 1
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
            INSERT INTO projects (name, description, technologies, url, start_date, end_date, user_id)
            VALUES (?, ?, ?, ?, ?, ?, 1)
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
        return fetch_one(conn, "projects", cursor.lastrowid, Project)


@router.get("/{proj_id}", response_model=Project)
async def get_project(proj_id: int):
    with get_db() as conn:
        return get_or_404(conn, "projects", proj_id, "Project", Project)


@router.put("/{proj_id}", response_model=Project)
async def update_project(proj_id: int, proj: ProjectUpdate):
    with get_db() as conn:
        exists_or_404(conn, "projects", proj_id, "Project")

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
        return fetch_one(conn, "projects", proj_id, Project)


@router.delete("/{proj_id}")
async def delete_project(proj_id: int):
    with get_db() as conn:
        exists_or_404(conn, "projects", proj_id, "Project")
        conn.execute("DELETE FROM projects WHERE id = ?", (proj_id,))
        conn.commit()
        return {"deleted": proj_id}
