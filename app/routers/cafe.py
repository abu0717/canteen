from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.cafe_schema import (
    CafeResponseSchema, CafeCreateSchema, CafeUpdateSchema,
    CafeCategoryCreateSchema, CafeCategoryResponseSchema,
    CafeMenuItemCreateSchema, CafeMenuItemUpdateSchema, CafeMenuItemResponseSchema,
    CafeInventoryCreateSchema, CafeInventoryUpdateSchema, CafeInventoryResponseSchema,
    PublicCategoryResponseSchema, PublicCategoryCreateSchema, PublicCategoryUpdateSchema
)
from app.routers.auth import get_current_user
from uuid import uuid4
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import text

router = APIRouter(
    prefix="/cafes",
    tags=["Cafes"],
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


@router.post("/", response_model=CafeResponseSchema)
def create_cafe(cafe: CafeCreateSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cafe_id = str(uuid4())
    owner_id = current_user["id"]
    db.execute(text("""
                    INSERT INTO cafe (id, name, location, image, owner_id, created_at, updated_at)
                    VALUES (:id, :name, :location, :image, :owner_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                   "id": cafe_id,
                   "name": cafe.name,
                   "location": cafe.location,
                   "image": cafe.image,
                   "owner_id": owner_id,
               })

    result = db.execute(text("""
                             SELECT id, name, location, image, owner_id, rating, created_at, updated_at
                             FROM cafe
                             WHERE id = :id
                             """), {"id": cafe_id}).mappings().fetchone()

    db.commit()

    return format_cafe_response(result)


@router.get("/", response_model=list[CafeResponseSchema])
def get_cafes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = text("""
                 SELECT id,
                        name,
                        location,
                        image,
                        owner_id,
                        rating,
                        COALESCE(created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM cafe
                 WHERE owner_id = :owner_id;
                 """)

    result = db.execute(query, {"owner_id": current_user["id"]})

    rows = result.mappings().fetchall()

    return [format_cafe_response(row) for row in rows]


@router.get("/{cafe_id}", response_model=CafeResponseSchema)
def get_cafe(cafe_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = text("""
                 SELECT id,
                        name,
                        location,
                        image,
                        owner_id,
                        rating,
                        COALESCE(created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM cafe
                 WHERE id = :cafe_id
                   AND owner_id = :owner_id;
                 """)

    result = db.execute(query, {"cafe_id": cafe_id, "owner_id": current_user["id"]})
    row = result.mappings().fetchone()

    if not row:
        return None

    return format_cafe_response(row)


@router.put("/{cafe_id}", response_model=CafeResponseSchema)
def update_cafe(cafe_id: str, cafe: CafeUpdateSchema, db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    update_fields = []
    params = {"cafe_id": cafe_id, "owner_id": current_user["id"]}
    
    if cafe.name is not None:
        update_fields.append("name = :name")
        params["name"] = cafe.name
    if cafe.location is not None:
        update_fields.append("location = :location")
        params["location"] = cafe.location
    if cafe.image is not None:
        update_fields.append("image = :image")
        params["image"] = cafe.image
    
    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        query = text(f"""
                     UPDATE cafe
                     SET {", ".join(update_fields)}
                     WHERE id = :cafe_id
                       AND owner_id = :owner_id;
                     """)
        db.execute(query, params)

    result = db.execute(text("""
                             SELECT id, name, location, image, owner_id, rating, created_at, updated_at
                             FROM cafe
                             WHERE id = :cafe_id
                               AND owner_id = :owner_id;
                             """), {"cafe_id": cafe_id, "owner_id": current_user["id"]}).mappings().fetchone()

    db.commit()

    return format_cafe_response(result)


@router.get('/{cafe_id}/categories', response_model=list[CafeCategoryResponseSchema])
def get_cafe_categories(cafe_id: str, db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    query = text("""
                 SELECT cat.id,
                        cat.cafe_id,
                        cat.name
                 FROM category AS cat
                          JOIN cafe AS c ON cat.cafe_id = c.id
                 WHERE cat.cafe_id = :cafe_id
                   AND c.owner_id = :owner_id;
                 """)

    result = db.execute(query, {"cafe_id": cafe_id, "owner_id": current_user["id"]})
    if result:
        row = result.mappings().fetchall()
    else:
        return None
    return row


@router.get("/public-categories", response_model=List[PublicCategoryResponseSchema])
def get_public_categories(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        query = text("""
                     SELECT id, name, image
                     FROM public_category
                     ORDER BY name
                     """)
        result = db.execute(query)
        rows = result.mappings().fetchall()
        
        if not rows:
            return []
        
        return [
            {
                "id": str(row["id"]), 
                "name": row["name"], 
                "image": format_image_url(row["image"])
            } 
            for row in rows
        ]
    except Exception as e:
        print(f"Error fetching public categories: {e}")
        return []


@router.post("/categories", response_model=CafeCategoryResponseSchema)
def create_cafe_category(category: CafeCategoryCreateSchema, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    category_id = str(uuid4())

    db.execute(text("""
                    INSERT INTO category (id, cafe_id, name)
                    VALUES (:id, :cafe_id, :name)
                    """), {
                   "id": category_id,
                   "cafe_id": category.cafe_id,
                   "name": category.name,
               })

    result = db.execute(text("""
                             SELECT id, cafe_id, name
                             FROM category
                             WHERE id = :id
                             """), {"id": category_id}).mappings().fetchone()

    db.commit()

    return result


@router.post("/menu", response_model=CafeMenuItemResponseSchema)
def create_cafe_menu_item(menu_item: CafeMenuItemCreateSchema, db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    cafe_check = db.execute(text("""
                                 SELECT id FROM cafe 
                                 WHERE id = :cafe_id AND owner_id = :owner_id
                                 """), {"cafe_id": menu_item.cafe_id, "owner_id": current_user["id"]}).fetchone()

    if not cafe_check:
        raise HTTPException(status_code=404, detail="Cafe not found")

    menu_item_id = str(uuid4())

    db.execute(text("""
                    INSERT INTO menu_item (id, cafe_id, category_id, image, name, description, price, available, created_at, updated_at)
                    VALUES (:id, :cafe_id, :category_id, :image, :name, :description, :price, :available, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                   "id": menu_item_id,
                   "cafe_id": menu_item.cafe_id,
                   "category_id": menu_item.category_id,
                   "image": menu_item.image,
                   "name": menu_item.name,
                   "description": menu_item.description,
                   "price": menu_item.price,
                   "available": menu_item.available,
               })

    result = db.execute(text("""
                             SELECT id, cafe_id, category_id, image, name, description, price, available, created_at, updated_at
                             FROM menu_item
                             WHERE id = :id
                             """), {"id": menu_item_id}).mappings().fetchone()

    db.commit()

    return format_menu_item_response(result)


@router.get("/{cafe_id}/menu", response_model=list[CafeMenuItemResponseSchema])
def get_cafe_menu_items(cafe_id: str, db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    query = text("""
                 SELECT m.id, m.cafe_id, m.category_id, m.image, m.name, m.description, m.price, m.available,
                        COALESCE(m.created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(m.updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM menu_item AS m
                 JOIN cafe AS c ON m.cafe_id = c.id
                 WHERE m.cafe_id = :cafe_id AND c.owner_id = :owner_id
                 """)

    result = db.execute(query, {"cafe_id": cafe_id, "owner_id": current_user["id"]})
    rows = result.mappings().fetchall()

    return [format_menu_item_response(row) for row in rows]


@router.get("/menu/{menu_item_id}", response_model=CafeMenuItemResponseSchema)
def get_menu_item(menu_item_id: str, db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    query = text("""
                 SELECT m.id, m.cafe_id, m.category_id, m.image, m.name, m.description, m.price, m.available,
                        COALESCE(m.created_at, CURRENT_TIMESTAMP) AS created_at,
                        COALESCE(m.updated_at, CURRENT_TIMESTAMP) AS updated_at
                 FROM menu_item AS m
                 JOIN cafe AS c ON m.cafe_id = c.id
                 WHERE m.id = :menu_item_id AND c.owner_id = :owner_id
                 """)

    result = db.execute(query, {"menu_item_id": menu_item_id, "owner_id": current_user["id"]})
    row = result.mappings().fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return format_menu_item_response(row)


@router.put("/menu/{menu_item_id}", response_model=CafeMenuItemResponseSchema)
def update_menu_item(menu_item_id: str, menu_item: CafeMenuItemUpdateSchema,
                     db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    check_query = text("""
                       SELECT m.id FROM menu_item AS m
                       JOIN cafe AS c ON m.cafe_id = c.id
                       WHERE m.id = :menu_item_id AND c.owner_id = :owner_id
                       """)

    check_result = db.execute(check_query, {"menu_item_id": menu_item_id, "owner_id": current_user["id"]}).fetchone()

    if not check_result:
        raise HTTPException(status_code=404, detail="Menu item not found")

    update_fields = []
    params = {"menu_item_id": menu_item_id}

    if menu_item.category_id is not None:
        update_fields.append("category_id = :category_id")
        params["category_id"] = menu_item.category_id
    if menu_item.image is not None:
        update_fields.append("image = :image")
        params["image"] = menu_item.image
    if menu_item.name is not None:
        update_fields.append("name = :name")
        params["name"] = menu_item.name
    if menu_item.description is not None:
        update_fields.append("description = :description")
        params["description"] = menu_item.description
    if menu_item.price is not None:
        update_fields.append("price = :price")
        params["price"] = menu_item.price
    if menu_item.available is not None:
        update_fields.append("available = :available")
        params["available"] = menu_item.available

    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_query = f"UPDATE menu_item SET {', '.join(update_fields)} WHERE id = :menu_item_id"
        db.execute(text(update_query), params)

    result = db.execute(text("""
                             SELECT id, cafe_id, category_id, image, name, description, price, available, created_at, updated_at
                             FROM menu_item
                             WHERE id = :menu_item_id
                             """), {"menu_item_id": menu_item_id}).mappings().fetchone()

    db.commit()

    return format_menu_item_response(result)


@router.delete("/menu/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(menu_item_id: str, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    check_query = text("""
                       SELECT m.id FROM menu_item AS m
                       JOIN cafe AS c ON m.cafe_id = c.id
                       WHERE m.id = :menu_item_id AND c.owner_id = :owner_id
                       """)

    check_result = db.execute(check_query, {"menu_item_id": menu_item_id, "owner_id": current_user["id"]}).fetchone()

    if not check_result:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.execute(text("DELETE FROM menu_item WHERE id = :menu_item_id"), {"menu_item_id": menu_item_id})
    db.commit()


@router.post("/inventory", response_model=CafeInventoryResponseSchema)
def create_inventory_item(inventory: CafeInventoryCreateSchema, db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    cafe_check = db.execute(text("""
                                 SELECT id FROM cafe 
                                 WHERE id = :cafe_id AND owner_id = :owner_id
                                 """), {"cafe_id": inventory.cafe_id, "owner_id": current_user["id"]}).fetchone()

    if not cafe_check:
        raise HTTPException(status_code=404, detail="Cafe not found")

    inventory_id = str(uuid4())

    db.execute(text("""
                    INSERT INTO inventory (id, cafe_id, name, quantity, kg, description, cafe_owner_id)
                    VALUES (:id, :cafe_id, :name, :quantity, :kg, :description, :cafe_owner_id)
                    """), {
                   "id": inventory_id,
                   "cafe_id": inventory.cafe_id,
                   "name": inventory.name,
                   "quantity": inventory.quantity,
                   "kg": inventory.kg,
                   "description": inventory.description,
                   "cafe_owner_id": inventory.cafe_owner_id,
               })

    result = db.execute(text("""
                             SELECT id, cafe_id, name, quantity, kg, description, cafe_owner_id
                             FROM inventory
                             WHERE id = :id
                             """), {"id": inventory_id}).mappings().fetchone()

    db.commit()

    return result


@router.get("/{cafe_id}/inventory", response_model=list[CafeInventoryResponseSchema])
def get_cafe_inventory(cafe_id: str, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    query = text("""
                 SELECT i.id, i.cafe_id, i.name, i.quantity, i.kg, i.description, i.cafe_owner_id
                 FROM inventory AS i
                 JOIN cafe AS c ON i.cafe_id = c.id
                 WHERE i.cafe_id = :cafe_id AND c.owner_id = :owner_id
                 """)

    result = db.execute(query, {"cafe_id": cafe_id, "owner_id": current_user["id"]})
    rows = result.mappings().fetchall()

    return rows


@router.put("/inventory/{inventory_id}", response_model=CafeInventoryResponseSchema)
def update_inventory_item(inventory_id: str, inventory: CafeInventoryUpdateSchema,
                          db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "cafe_owner":
        check_query = text("""
                           SELECT i.id FROM inventory AS i
                           JOIN cafe AS c ON i.cafe_id = c.id
                           WHERE i.id = :inventory_id AND c.owner_id = :owner_id
                           """)
        check_result = db.execute(check_query, {"inventory_id": inventory_id, "owner_id": current_user["id"]}).fetchone()
    elif current_user["role"] == "cafe_worker":
        check_query = text("""
                           SELECT i.id FROM inventory AS i
                           JOIN cafe_worker AS cw ON i.cafe_id = cw.cafe_id
                           WHERE i.id = :inventory_id AND cw.user_id = :user_id
                           """)
        check_result = db.execute(check_query, {"inventory_id": inventory_id, "user_id": current_user["id"]}).fetchone()
    else:
        raise HTTPException(status_code=403, detail="Only cafe owners and workers can update inventory")

    if not check_result:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    update_fields = []
    params = {"inventory_id": inventory_id}

    if inventory.name is not None:
        update_fields.append("name = :name")
        params["name"] = inventory.name
    if inventory.quantity is not None:
        update_fields.append("quantity = :quantity")
        params["quantity"] = inventory.quantity
    if inventory.kg is not None:
        update_fields.append("kg = :kg")
        params["kg"] = inventory.kg
    if inventory.description is not None:
        update_fields.append("description = :description")
        params["description"] = inventory.description
    if inventory.cafe_owner_id is not None:
        update_fields.append("cafe_owner_id = :cafe_owner_id")
        params["cafe_owner_id"] = inventory.cafe_owner_id

    if update_fields:
        update_query = f"UPDATE inventory SET {', '.join(update_fields)} WHERE id = :inventory_id"
        db.execute(text(update_query), params)

    result = db.execute(text("""
                             SELECT id, cafe_id, name, quantity, kg, description, cafe_owner_id
                             FROM inventory
                             WHERE id = :inventory_id
                             """), {"inventory_id": inventory_id}).mappings().fetchone()

    db.commit()

    return result


@router.delete("/inventory/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(inventory_id: str, db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    check_query = text("""
                       SELECT i.id FROM inventory AS i
                       JOIN cafe AS c ON i.cafe_id = c.id
                       WHERE i.id = :inventory_id AND c.owner_id = :owner_id
                       """)

    check_result = db.execute(check_query, {"inventory_id": inventory_id, "owner_id": current_user["id"]}).fetchone()

    if not check_result:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    db.execute(text("DELETE FROM inventory WHERE id = :inventory_id"), {"inventory_id": inventory_id})
    db.commit()
