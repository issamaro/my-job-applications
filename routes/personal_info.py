from fastapi import APIRouter
from database import get_db
from schemas import User, UserUpdate

router = APIRouter(prefix="/api/personal-info", tags=["personal-info"])


@router.get("", response_model=User | None)
async def get_personal_info():
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM users WHERE id = 1")
        row = cursor.fetchone()
        if row is None:
            return None
        return User.model_validate(dict(row))


@router.put("", response_model=User)
async def update_personal_info(info: UserUpdate):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM users WHERE id = 1")
        exists = cursor.fetchone() is not None

        if exists:
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
                    info.full_name,
                    info.email,
                    info.phone,
                    info.location,
                    info.linkedin_url,
                    info.summary,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO users (id, full_name, email, phone, location, linkedin_url, summary)
                VALUES (1, ?, ?, ?, ?, ?, ?)
                """,
                (
                    info.full_name,
                    info.email,
                    info.phone,
                    info.location,
                    info.linkedin_url,
                    info.summary,
                ),
            )
        conn.commit()

        cursor = conn.execute("SELECT * FROM users WHERE id = 1")
        row = cursor.fetchone()
        return User.model_validate(dict(row))
