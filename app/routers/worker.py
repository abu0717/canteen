from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.routers.auth import get_current_user
from pydantic import BaseModel
from typing import List
from uuid import uuid4


router = APIRouter(
    prefix="/workers",
    tags=["Workers"],
)


def format_image_url(image_path: str | None) -> str | None:
    """Return image path as-is."""
    return image_path


class CafeWorkerCreateSchema(BaseModel):
    user_id: str
    cafe_id: str


class CafeWorkerResponseSchema(BaseModel):
    id: str
    user_id: str
    cafe_id: str
    user_name: str
    user_email: str
    cafe_name: str


@router.post("/", response_model=CafeWorkerResponseSchema)
def assign_worker_to_cafe(
    worker: CafeWorkerCreateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Get the cafe_owner_profile.id for this user
    owner_profile = db.execute(
        text("SELECT id FROM cafe_owner_profile WHERE user_id = :user_id"),
        {"user_id": current_user["id"]}
    ).fetchone()
    
    if not owner_profile:
        raise HTTPException(status_code=403, detail="Only cafe owners can assign workers")
    
    cafe_check = db.execute(
        text("SELECT id, name FROM cafe WHERE id = :cafe_id AND owner_id = :owner_id"),
        {"cafe_id": worker.cafe_id, "owner_id": owner_profile[0]}
    ).fetchone()

    if not cafe_check:
        raise HTTPException(status_code=404, detail="Cafe not found or you don't have access")

    user_check = db.execute(
        text("SELECT id, name, email, role FROM users WHERE id = :user_id"),
        {"user_id": worker.user_id}
    ).fetchone()

    if not user_check:
        raise HTTPException(status_code=404, detail="User not found")

    if user_check[3] != "cafe_worker":
        raise HTTPException(status_code=400, detail="User must have cafe_worker role")

    existing = db.execute(
        text("SELECT id FROM cafe_worker WHERE user_id = :user_id AND cafe_id = :cafe_id"),
        {"user_id": worker.user_id, "cafe_id": worker.cafe_id}
    ).fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="Worker already assigned to this cafe")

    worker_id = str(uuid4())

    db.execute(
        text("""
            INSERT INTO cafe_worker (id, user_id, cafe_id, created_at, updated_at)
            VALUES (:id, :user_id, :cafe_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """),
        {"id": worker_id, "user_id": worker.user_id, "cafe_id": worker.cafe_id}
    )

    db.commit()

    return {
        "id": worker_id,
        "user_id": user_check[0],
        "cafe_id": cafe_check[0],
        "user_name": user_check[1],
        "user_email": user_check[2],
        "cafe_name": cafe_check[1]
    }


@router.get("/cafe/{cafe_id}", response_model=List[CafeWorkerResponseSchema])
def get_cafe_workers(
    cafe_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Get the cafe_owner_profile.id for this user
    owner_profile = db.execute(
        text("SELECT id FROM cafe_owner_profile WHERE user_id = :user_id"),
        {"user_id": current_user["id"]}
    ).fetchone()
    
    if not owner_profile:
        raise HTTPException(status_code=403, detail="Only cafe owners can view workers")
    
    cafe_check = db.execute(
        text("SELECT id FROM cafe WHERE id = :cafe_id AND owner_id = :owner_id"),
        {"cafe_id": cafe_id, "owner_id": owner_profile[0]}
    ).fetchone()

    if not cafe_check:
        raise HTTPException(status_code=404, detail="Cafe not found or you don't have access")

    workers = db.execute(
        text("""
            SELECT cw.id, cw.user_id, cw.cafe_id, u.name as user_name, u.email as user_email, c.name as cafe_name
            FROM cafe_worker cw
            JOIN users u ON cw.user_id = u.id
            JOIN cafe c ON cw.cafe_id = c.id
            WHERE cw.cafe_id = :cafe_id
        """),
        {"cafe_id": cafe_id}
    ).mappings().fetchall()

    return workers


@router.get("/my-cafes", response_model=List[dict])
def get_worker_cafes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "cafe_worker":
        raise HTTPException(status_code=403, detail="Only cafe workers can access this endpoint")

    cafes = db.execute(
        text("""
            SELECT c.id, c.name, c.location, c.image, cw.id as assignment_id
            FROM cafe_worker cw
            JOIN cafe c ON cw.cafe_id = c.id
            WHERE cw.user_id = :user_id
        """),
        {"user_id": current_user["id"]}
    ).mappings().fetchall()
    
    # Format image URLs
    formatted_cafes = []
    for cafe in cafes:
        cafe_dict = dict(cafe)
        cafe_dict['image'] = format_image_url(cafe_dict.get('image'))
        formatted_cafes.append(cafe_dict)
    
    cafes = formatted_cafes

    return cafes


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_worker_from_cafe(
    worker_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Get the cafe_owner_profile.id for this user
    owner_profile = db.execute(
        text("SELECT id FROM cafe_owner_profile WHERE user_id = :user_id"),
        {"user_id": current_user["id"]}
    ).fetchone()
    
    if not owner_profile:
        raise HTTPException(status_code=403, detail="Only cafe owners can remove workers")
    
    worker_check = db.execute(
        text("""
            SELECT cw.id FROM cafe_worker cw
            JOIN cafe c ON cw.cafe_id = c.id
            WHERE cw.id = :worker_id AND c.owner_id = :owner_id
        """),
        {"worker_id": worker_id, "owner_id": owner_profile[0]}
    ).fetchone()

    if not worker_check:
        raise HTTPException(status_code=404, detail="Worker assignment not found or you don't have access")

    db.execute(
        text("DELETE FROM cafe_worker WHERE id = :worker_id"),
        {"worker_id": worker_id}
    )

    db.commit()

