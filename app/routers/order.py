from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.routers.auth import get_current_user
from app.schemas.order_schema import (
    OrderCreateSchema, OrderUpdateSchema, OrderResponseSchema,
    OrderDetailResponseSchema, OrderItemResponseSchema
)
from app.models.order import StatusTypes

UZBEKISTAN_TZ = timezone(timedelta(hours=5))
from app.websockets.connection_manager import manager

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/", response_model=OrderDetailResponseSchema)
async def create_order(order: OrderCreateSchema, db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    cafe_check = db.execute(text("SELECT id FROM cafe WHERE id = :cafe_id"),
                           {"cafe_id": order.cafe_id}).fetchone()

    if not cafe_check:
        raise HTTPException(status_code=404, detail="Cafe not found")

    total_price = 0.0
    for item in order.items:
        menu_item = db.execute(text("""
                                    SELECT price, available FROM menu_item 
                                    WHERE id = :menu_item_id AND cafe_id = :cafe_id
                                    """),
                              {"menu_item_id": item.menu_item_id, "cafe_id": order.cafe_id}).fetchone()

        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item.menu_item_id} not found")

        if not menu_item[1]:
            raise HTTPException(status_code=400, detail=f"Menu item {item.menu_item_id} is not available")

        total_price += menu_item[0] * item.quantity

    # Get current time in Uzbekistan timezone
    now_uzbekistan = datetime.now(UZBEKISTAN_TZ)

    order_result = db.execute(text("""
                                   INSERT INTO "order" (account_id, cafe_id, note, status, total_price, created_at, updated_at)
                                   VALUES (:account_id, :cafe_id, :note, :status, :total_price, :created_at, :updated_at)
                                   RETURNING id
                                   """), {
                              "account_id": current_user["id"],
                              "cafe_id": order.cafe_id,
                              "note": order.note,
                              "status": StatusTypes.pending.value,
                              "total_price": total_price,
                              "created_at": now_uzbekistan,
                              "updated_at": now_uzbekistan,
                          })

    order_id = order_result.fetchone()[0]

    order_items = []
    for item in order.items:
        menu_item = db.execute(text("SELECT price FROM menu_item WHERE id = :menu_item_id"),
                              {"menu_item_id": item.menu_item_id}).fetchone()

        item_result = db.execute(text("""
                                      INSERT INTO order_item (order_id, menu_item_id, quantity, price, scheduled, scheduled_time, created_at, updated_at)
                                      VALUES (:order_id, :menu_item_id, :quantity, :price, :scheduled, :scheduled_time, :created_at, :updated_at)
                                      RETURNING id, order_id, menu_item_id, quantity, price, scheduled, scheduled_time, created_at, updated_at
                                      """), {
                                 "order_id": order_id,
                                 "menu_item_id": item.menu_item_id,
                                 "quantity": item.quantity,
                                 "price": menu_item[0],
                                 "scheduled": item.scheduled if hasattr(item, 'scheduled') else False,
                                 "scheduled_time": item.scheduled_time if hasattr(item, 'scheduled_time') else None,
                                 "created_at": now_uzbekistan,
                                 "updated_at": now_uzbekistan,
                             }).mappings().fetchone()

        order_items.append(item_result)

    db.commit()

    order_data = db.execute(text("""
                                 SELECT o.id, o.account_id, o.cafe_id, o.note, o.status, o.total_price, 
                                        o.created_at, o.updated_at,
                                        u.name as account_name,
                                        c.name as cafe_name
                                 FROM "order" o
                                 JOIN users u ON o.account_id = u.id
                                 JOIN cafe c ON o.cafe_id = c.id
                                 WHERE o.id = :order_id
                                 """), {"order_id": order_id}).mappings().fetchone()

    # Add menu_item_name to items
    items_with_names = []
    for item in order_items:
        item_dict = dict(item)
        menu_name = db.execute(text("SELECT name FROM menu_item WHERE id = :id"), 
                              {"id": item_dict["menu_item_id"]}).fetchone()
        item_dict["menu_item_name"] = menu_name[0] if menu_name else ""
        items_with_names.append(item_dict)

    result = {
        **dict(order_data),
        "items": items_with_names
    }

    await manager.broadcast_to_cafe(order.cafe_id, {
        "type": "new_order",
        "order_id": order_id,
        "customer_name": current_user["name"],
        "total_price": total_price,
        "status": StatusTypes.pending.value,
        "items_count": len(order.items),
        "note": order.note,
        "created_at": str(order_data["created_at"])
    })

    return result


@router.get("/", response_model=list[OrderResponseSchema])
def get_user_orders(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = text("""
                 SELECT id, account_id, cafe_id, note, status, total_price, created_at, updated_at
                 FROM "order"
                 WHERE account_id = :account_id
                 ORDER BY created_at DESC
                 """)

    result = db.execute(query, {"account_id": current_user["id"]})
    rows = result.mappings().fetchall()

    return rows


@router.get("/history", response_model=list[OrderDetailResponseSchema])
def get_history(db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    orders = db.execute(text("""
                             SELECT o.id, o.account_id, o.cafe_id, o.note, o.status, o.total_price, 
                                    o.created_at, o.updated_at,
                                    u.name as account_name,
                                    c.name as cafe_name
                             FROM "order" o
                             JOIN users u ON o.account_id = u.id
                             JOIN cafe c ON o.cafe_id = c.id
                             WHERE o.account_id = :account_id AND o.status = :status_completed
                             ORDER BY o.created_at DESC
                             """), {
                                "account_id": current_user["id"],
                                "status_completed": StatusTypes.completed.value
                            }).mappings().fetchall()
    result = []
    for order in orders:
        order_items = db.execute(text("""
                                      SELECT oi.id, oi.order_id, oi.menu_item_id, oi.quantity, oi.price, 
                                             oi.scheduled, oi.scheduled_time, oi.created_at, oi.updated_at,
                                             m.name as menu_item_name
                                      FROM order_item oi
                                      JOIN menu_item m ON oi.menu_item_id = m.id
                                      WHERE oi.order_id = :order_id
                                      """), {"order_id": order["id"]}).mappings().fetchall()

        result.append({
            **dict(order),
            "items": [dict(item) for item in order_items]
        })
    return result


@router.get("/{order_id}", response_model=OrderDetailResponseSchema)
def get_order(order_id: int, db: Session = Depends(get_db),
              current_user: dict = Depends(get_current_user)):
    order_data = db.execute(text("""
                                 SELECT o.id, o.account_id, o.cafe_id, o.note, o.status, o.total_price, 
                                        o.created_at, o.updated_at,
                                        u.name as account_name,
                                        c.name as cafe_name
                                 FROM "order" o
                                 JOIN user u ON o.account_id = u.id
                                 JOIN cafe c ON o.cafe_id = c.id
                                 WHERE o.id = :order_id AND o.account_id = :account_id
                                 """),
                           {"order_id": order_id, "account_id": current_user["id"]}).mappings().fetchone()

    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = db.execute(text("""
                                  SELECT oi.id, oi.order_id, oi.menu_item_id, oi.quantity, oi.price, 
                                         oi.scheduled, oi.scheduled_time, oi.created_at, oi.updated_at,
                                         m.name as menu_item_name
                                  FROM order_item oi
                                  JOIN menu_item m ON oi.menu_item_id = m.id
                                  WHERE oi.order_id = :order_id
                                  """), {"order_id": order_id}).mappings().fetchall()

    return {
        **dict(order_data),
        "items": [dict(item) for item in order_items]
    }


@router.get("/cafe/{cafe_id}", response_model=list[OrderDetailResponseSchema])
def get_cafe_orders(cafe_id: str, db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "cafe_owner":
        cafe_check = db.execute(text("""
                                     SELECT id FROM cafe 
                                     WHERE id = :cafe_id AND owner_id = :owner_id
                                     """), {"cafe_id": cafe_id, "owner_id": current_user["id"]}).fetchone()
    elif current_user["role"] == "cafe_worker":
        cafe_check = db.execute(text("""
                                     SELECT c.id FROM cafe c
                                     JOIN cafe_worker cw ON c.id = cw.cafe_id
                                     WHERE c.id = :cafe_id AND cw.user_id = :user_id
                                     """), {"cafe_id": cafe_id, "user_id": current_user["id"]}).fetchone()
    else:
        raise HTTPException(status_code=403, detail="Only cafe owners and workers can access orders")

    if not cafe_check:
        raise HTTPException(status_code=404, detail="Cafe not found or you don't have access")

    orders = db.execute(text("""
                             SELECT o.id, o.account_id, o.cafe_id, o.note, o.status, o.total_price, 
                                    o.created_at, o.updated_at,
                                    u.name as account_name,
                                    c.name as cafe_name
                             FROM "order" o
                             JOIN user u ON o.account_id = u.id
                             JOIN cafe c ON o.cafe_id = c.id
                             WHERE o.cafe_id = :cafe_id
                             ORDER BY o.created_at DESC
                             """), {"cafe_id": cafe_id}).mappings().fetchall()

    result = []
    for order in orders:
        order_items = db.execute(text("""
                                      SELECT oi.id, oi.order_id, oi.menu_item_id, oi.quantity, oi.price, 
                                             oi.scheduled, oi.scheduled_time, oi.created_at, oi.updated_at,
                                             m.name as menu_item_name
                                      FROM order_item oi
                                      JOIN menu_item m ON oi.menu_item_id = m.id
                                      WHERE oi.order_id = :order_id
                                      """), {"order_id": order["id"]}).mappings().fetchall()

        result.append({
            **dict(order),
            "items": [dict(item) for item in order_items]
        })

    return result


@router.put("/{order_id}", response_model=OrderResponseSchema)
async def update_order_status(order_id: int, order_update: OrderUpdateSchema,
                        db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "cafe_owner":
        order_check = db.execute(text("""
                                      SELECT o.id, o.account_id, o.cafe_id FROM "order" AS o
                                      JOIN cafe AS c ON o.cafe_id = c.id
                                      WHERE o.id = :order_id AND c.owner_id = :owner_id
                                      """),
                                {"order_id": order_id, "owner_id": current_user["id"]}).fetchone()
    elif current_user["role"] == "cafe_worker":
        order_check = db.execute(text("""
                                      SELECT o.id, o.account_id, o.cafe_id FROM "order" AS o
                                      JOIN cafe_worker AS cw ON o.cafe_id = cw.cafe_id
                                      WHERE o.id = :order_id AND cw.user_id = :user_id
                                      """),
                                {"order_id": order_id, "user_id": current_user["id"]}).fetchone()
    else:
        raise HTTPException(status_code=403, detail="Only cafe owners and workers can update orders")

    if not order_check:
        raise HTTPException(status_code=404, detail="Order not found or you don't have access")

    update_fields = []
    params = {"order_id": order_id}

    if order_update.status is not None:
        update_fields.append("status = :status")
        params["status"] = order_update.status.value
    if order_update.note is not None:
        update_fields.append("note = :note")
        params["note"] = order_update.note

    if update_fields:
        now_uzbekistan = datetime.now(UZBEKISTAN_TZ)
        update_fields.append("updated_at = :updated_at")
        params["updated_at"] = now_uzbekistan
        update_query = f'UPDATE "order" SET {", ".join(update_fields)} WHERE id = :order_id'
        db.execute(text(update_query), params)

    result = db.execute(text("""
                             SELECT id, account_id, cafe_id, note, status, total_price, created_at, updated_at
                             FROM "order"
                             WHERE id = :order_id
                             """), {"order_id": order_id}).mappings().fetchone()

    db.commit()

    if order_update.status:
        await manager.send_to_user(order_check[1], {
            "type": "order_status_update",
            "order_id": order_id,
            "status": order_update.status.value,
            "updated_by": current_user["name"]
        })

    return result


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(order_id: int, db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    order_data = db.execute(text("""
                                 SELECT id, status FROM "order"
                                 WHERE id = :order_id AND account_id = :account_id
                                 """),
                           {"order_id": order_id, "account_id": current_user["id"]}).fetchone()

    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")

    if order_data[1] in [StatusTypes.completed.value, StatusTypes.cancelled.value]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or already cancelled order")

    db.execute(text("""
                    UPDATE "order" 
                    SET status = :status, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :order_id
                    """),
              {"order_id": order_id, "status": StatusTypes.cancelled.value})
    db.commit()
