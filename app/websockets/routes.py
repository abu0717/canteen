from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.websockets.connection_manager import manager
from jose import jwt, JWTError
from app.config import settings

router = APIRouter()


async def get_current_user_ws(token: str, db: Session):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("user_id")
        if user_id is None:
            return None

        result = db.execute(
            text("SELECT id, name, email, role FROM user WHERE id = :id"),
            {"id": user_id}
        ).mappings().fetchone()

        if result is None:
            return None

        return result

    except JWTError:
        return None


@router.websocket("/ws/cafe/{cafe_id}")
async def websocket_cafe_endpoint(
    websocket: WebSocket,
    cafe_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_ws(token, db)

    if not current_user:
        await websocket.close(code=1008)
        return

    user_role = current_user["role"]
    user_id = current_user["id"]

    if user_role not in ["cafe_owner", "cafe_worker", "admin"]:
        await websocket.close(code=1008)
        return

    if user_role == "cafe_owner":
        cafe_check = db.execute(
            text("SELECT id FROM cafe WHERE id = :cafe_id AND owner_id = :owner_id"),
            {"cafe_id": cafe_id, "owner_id": user_id}
        ).fetchone()

        if not cafe_check:
            await websocket.close(code=1008)
            return

    elif user_role == "cafe_worker":
        worker_check = db.execute(
            text("SELECT id FROM cafe_worker WHERE cafe_id = :cafe_id AND user_id = :user_id"),
            {"cafe_id": cafe_id, "user_id": user_id}
        ).fetchone()

        if not worker_check:
            await websocket.close(code=1008)
            return

    await manager.connect(websocket, cafe_id, user_id)

    try:
        await manager.send_personal_message({
            "type": "connection",
            "message": f"Connected to cafe {cafe_id}",
            "user": current_user["name"]
        }, websocket)

        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message({
                "type": "echo",
                "message": data
            }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, cafe_id, user_id)


@router.websocket("/ws/orders")
async def websocket_orders_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_ws(token, db)

    if not current_user:
        await websocket.close(code=1008)
        return

    user_id = current_user["id"]

    await manager.connect(websocket, f"user_{user_id}", user_id)

    try:
        await manager.send_personal_message({
            "type": "connection",
            "message": "Connected to order updates",
            "user": current_user["name"]
        }, websocket)

        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message({
                "type": "echo",
                "message": data
            }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, f"user_{user_id}", user_id)

