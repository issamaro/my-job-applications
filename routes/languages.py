from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db
from schemas import Language, LanguageCreate, LanguageUpdate

router = APIRouter(prefix="/api/languages", tags=["languages"])


class ReorderItem(BaseModel):
    id: int
    display_order: int


@router.get("", response_model=list[Language])
async def list_languages():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM languages
            ORDER BY display_order ASC, id ASC
            """
        )
        rows = cursor.fetchall()
        return [Language.model_validate(dict(row)) for row in rows]


@router.post("", response_model=Language)
async def create_language(lang: LanguageCreate):
    with get_db() as conn:
        cursor = conn.execute("SELECT COALESCE(MAX(display_order), -1) + 1 FROM languages")
        next_order = cursor.fetchone()[0]

        cursor = conn.execute(
            """
            INSERT INTO languages (name, level, display_order)
            VALUES (?, ?, ?)
            """,
            (lang.name, lang.level.value, next_order),
        )
        conn.commit()
        lang_id = cursor.lastrowid

        cursor = conn.execute("SELECT * FROM languages WHERE id = ?", (lang_id,))
        row = cursor.fetchone()
        return Language.model_validate(dict(row))


@router.put("/reorder", response_model=list[Language])
async def reorder_languages(items: list[ReorderItem]):
    with get_db() as conn:
        for item in items:
            conn.execute(
                "UPDATE languages SET display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (item.display_order, item.id),
            )
        conn.commit()

        cursor = conn.execute(
            """
            SELECT * FROM languages
            ORDER BY display_order ASC, id ASC
            """
        )
        rows = cursor.fetchall()
        return [Language.model_validate(dict(row)) for row in rows]


@router.get("/{lang_id}", response_model=Language)
async def get_language(lang_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM languages WHERE id = ?", (lang_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Language not found")
        return Language.model_validate(dict(row))


@router.put("/{lang_id}", response_model=Language)
async def update_language(lang_id: int, lang: LanguageUpdate):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM languages WHERE id = ?", (lang_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Language not found")

        conn.execute(
            """
            UPDATE languages SET
                name = ?,
                level = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (lang.name, lang.level.value, lang_id),
        )
        conn.commit()

        cursor = conn.execute("SELECT * FROM languages WHERE id = ?", (lang_id,))
        row = cursor.fetchone()
        return Language.model_validate(dict(row))


@router.delete("/{lang_id}")
async def delete_language(lang_id: int):
    with get_db() as conn:
        cursor = conn.execute("SELECT id FROM languages WHERE id = ?", (lang_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Language not found")

        conn.execute("DELETE FROM languages WHERE id = ?", (lang_id,))
        conn.commit()
        return {"deleted": lang_id}
