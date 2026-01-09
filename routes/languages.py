from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db, get_or_404, exists_or_404, fetch_one
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
        return fetch_one(conn, "languages", cursor.lastrowid, Language)


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
        return get_or_404(conn, "languages", lang_id, "Language", Language)


@router.put("/{lang_id}", response_model=Language)
async def update_language(lang_id: int, lang: LanguageUpdate):
    with get_db() as conn:
        exists_or_404(conn, "languages", lang_id, "Language")

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
        return fetch_one(conn, "languages", lang_id, Language)


@router.delete("/{lang_id}")
async def delete_language(lang_id: int):
    with get_db() as conn:
        exists_or_404(conn, "languages", lang_id, "Language")
        conn.execute("DELETE FROM languages WHERE id = ?", (lang_id,))
        conn.commit()
        return {"deleted": lang_id}
