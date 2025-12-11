from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.cafe_schema import (
    CafeResponseSchema, CafeMenuItemResponseSchema, CafeCategoryResponseSchema,
    PublicCategoryCreateSchema, PublicCategoryResponseSchema, PublicCategoryUpdateSchema
)
from typing import List, Optional
import uuid
import shutil
from pathlib import Path

router = APIRouter(
    prefix="/public",
    tags=["Public"],
)


def format_image_url(image_path: str | None) -> str | None:
    """Return image path as-is."""
    return image_path


def format_cafe_response(row):
    """Format cafe response with full image URL."""
    if not row:
        return None
    data = dict(row)
    data['image'] = format_image_url(data.get('image'))
    return data


def format_menu_item_response(row):
    """Format menu item response with full image URL."""
    if not row:
        return None
    data = dict(row)
    data['image'] = format_image_url(data.get('image'))
    return data


@router.get("/cafes", response_model=List[CafeResponseSchema])
def get_all_cafes(db: Session = Depends(get_db)):
    query = text("""
                 SELECT id, name, location, image, owner_id, 
                        COALESCE(rating, 0.0) AS rating,
                        COALESCE(created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM cafe
                 """)
    result = db.execute(query)
    rows = result.mappings().fetchall()
    return [format_cafe_response(row) for row in rows]


@router.get("/cafes/{cafe_id}", response_model=CafeResponseSchema)
def get_cafe_details(cafe_id: str, db: Session = Depends(get_db)):
    query = text("""
                 SELECT id, name, location, image, owner_id, 
                        COALESCE(rating, 0.0) AS rating,
                        COALESCE(created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM cafe
                 WHERE id = :cafe_id
                 """)
    result = db.execute(query, {"cafe_id": cafe_id})
    row = result.mappings().fetchone()
    return format_cafe_response(row)


@router.get("/cafes/{cafe_id}/menu", response_model=List[CafeMenuItemResponseSchema])
def get_cafe_menu(cafe_id: str, db: Session = Depends(get_db)):
    query = text("""
                 SELECT id, cafe_id, category_id, image, name, description, price, available,
                        COALESCE(created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM menu_item
                 WHERE cafe_id = :cafe_id AND available = TRUE
                 """)
    result = db.execute(query, {"cafe_id": cafe_id})
    rows = result.mappings().fetchall()
    return [format_menu_item_response(row) for row in rows]


@router.get("/cafes/{cafe_id}/categories", response_model=List[CafeCategoryResponseSchema])
def get_cafe_categories(cafe_id: str, db: Session = Depends(get_db)):
    query = text("""
                 SELECT id, cafe_id, name
                 FROM category
                 WHERE cafe_id = :cafe_id
                 """)
    result = db.execute(query, {"cafe_id": cafe_id})
    rows = result.mappings().fetchall()
    return rows


@router.get("/categories/{category_id}/menu", response_model=List[CafeMenuItemResponseSchema])
def get_menu_items_by_category(category_id: str, db: Session = Depends(get_db)):
    query = text("""
                 SELECT id, cafe_id, category_id, image, name, description, price, available,
                        COALESCE(created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM menu_item
                 WHERE category_id = :category_id AND available = TRUE
                 """)
    result = db.execute(query, {"category_id": category_id})
    rows = result.mappings().fetchall()
    return [format_menu_item_response(row) for row in rows]

@router.get("/categories", response_model=List[PublicCategoryResponseSchema])
def get_all_categories(db: Session = Depends(get_db)):
    query = text("""
                 SELECT id, name, image
                 FROM public_category
                 """)
    result = db.execute(query)
    rows = result.mappings().fetchall()
    return rows

@router.get("/categories/{public_category_name}/cafes", response_model=List[CafeResponseSchema])
def get_cafes_by_public_category(public_category_name: str, db: Session = Depends(get_db)):
    """
    Get all cafes that have menu items matching the public category name.
    Searches for menu items where the name contains the category name.
    """
    query = text("""
                 SELECT DISTINCT c.id, c.name, c.location, c.image, c.owner_id, 
                        COALESCE(c.rating, 0.0) AS rating,
                        COALESCE(c.created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(c.updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM cafe c
                 JOIN menu_item m ON c.id = m.cafe_id
                 WHERE m.available = TRUE 
                   AND (LOWER(m.name) LIKE LOWER(:category_name) 
                        OR LOWER(m.description) LIKE LOWER(:category_name))
                 ORDER BY c.rating DESC
                 """)
    result = db.execute(query, {"category_name": f"%{public_category_name}%"})
    rows = result.mappings().fetchall()
    return [format_cafe_response(row) for row in rows]

@router.post("/categories", response_model=PublicCategoryResponseSchema)
async def create_public_category(
    name: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    category_id = str(uuid.uuid4())
    
    # Handle image upload if provided
    image_path = None
    if image:
        UPLOAD_DIR = Path("uploads")
        UPLOAD_DIR.mkdir(exist_ok=True)
        
        file_ext = Path(image.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_path = f"/uploads/{unique_filename}"
    
    db.execute(
        text("""
            INSERT INTO public_category (id, name, image)
            VALUES (:id, :name, :image)
        """),
        {"id": category_id, "name": name, "image": image_path}
    )
    db.commit()
    result = db.execute(
        text("""
            SELECT id, name, image
            FROM public_category
            WHERE id = :id
        """),
        {"id": category_id}
    )
    row = result.mappings().fetchone()
    return row

@router.put("/categories/{category_id}", response_model=PublicCategoryResponseSchema)
def update_public_category(
    category_id: str,
    category: PublicCategoryUpdateSchema,
    db: Session = Depends(get_db)
):
    db.execute(
        text("""
            UPDATE public_category
            SET name = COALESCE(:name, name),
                image = COALESCE(:image, image)
            WHERE id = :id
        """),
        {"id": category_id, "name": category.name, "image": category.image}
    )
    db.commit()
    result = db.execute(
        text("""
            SELECT id, name, image
            FROM public_category
            WHERE id = :id
        """),
        {"id": category_id}
    )
    row = result.mappings().fetchone()
    return row