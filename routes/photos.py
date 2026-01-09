from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import PhotoUpload, PhotoResponse

router = APIRouter(prefix="/api/photos", tags=["photos"])


@router.get("", response_model=PhotoResponse | None)
def get_photo():
    """Get the current photo data URL."""
    with get_db() as conn:
        row = conn.execute("SELECT photo FROM users WHERE id = 1").fetchone()
        if not row or not row["photo"]:
            return None
        return PhotoResponse(image_data=row["photo"])


@router.put("", response_model=PhotoResponse)
def upload_photo(photo: PhotoUpload):
    """Upload or replace photo."""
    with get_db() as conn:
        # Check if user exists
        row = conn.execute("SELECT id FROM users WHERE id = 1").fetchone()
        if not row:
            raise HTTPException(400, "Personal info must be created first")

        conn.execute(
            "UPDATE users SET photo = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (photo.image_data,),
        )
        conn.commit()
        return PhotoResponse(image_data=photo.image_data)


@router.delete("", status_code=204)
def delete_photo():
    """Delete photo."""
    with get_db() as conn:
        row = conn.execute("SELECT photo FROM users WHERE id = 1").fetchone()
        if not row or not row["photo"]:
            raise HTTPException(404, "Photo not found")

        conn.execute(
            "UPDATE users SET photo = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = 1"
        )
        conn.commit()
