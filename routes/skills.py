from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import Skill, SkillCreate

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=list[Skill])
async def list_skills():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM skills
            ORDER BY name ASC
            """
        )
        rows = cursor.fetchall()
        return [Skill.model_validate(dict(row)) for row in rows]


@router.post("", response_model=list[Skill])
async def create_skills(skill_input: SkillCreate):
    names = [name.strip() for name in skill_input.names.split(",") if name.strip()]
    created_skills = []

    with get_db() as conn:
        for name in names:
            cursor = conn.execute("SELECT * FROM skills WHERE name = ?", (name,))
            existing = cursor.fetchone()
            if existing:
                created_skills.append(Skill.model_validate(dict(existing)))
            else:
                cursor = conn.execute(
                    "INSERT INTO skills (name) VALUES (?)",
                    (name,),
                )
                skill_id = cursor.lastrowid
                created_skills.append(Skill(id=skill_id, name=name))
        conn.commit()

    return created_skills


@router.delete("/{skill_id}")
async def delete_skill(skill_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM skills WHERE id = ?", (skill_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Skill not found")

        conn.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
        conn.commit()
        return {"deleted": skill_id}
