from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import PersonalInfo, PersonalInfoUpdate

router = APIRouter(prefix="/api/personal-info", tags=["personal-info"])


@router.get("", response_model=PersonalInfo | None)
async def get_personal_info():
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM personal_info WHERE id = 1")
        row = cursor.fetchone()
        if row is None:
            return None
        return PersonalInfo.model_validate(dict(row))


@router.put("", response_model=PersonalInfo)
async def update_personal_info(info: PersonalInfoUpdate):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM personal_info WHERE id = 1")
        exists = cursor.fetchone() is not None

        if exists:
            conn.execute(
                """
                UPDATE personal_info SET
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
                INSERT INTO personal_info (id, full_name, email, phone, location, linkedin_url, summary)
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

        cursor = conn.execute("SELECT * FROM personal_info WHERE id = 1")
        row = cursor.fetchone()
        return PersonalInfo.model_validate(dict(row))
