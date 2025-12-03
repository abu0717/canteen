from typing import Dict, List, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, cafe_id: str, user_id: str):
        await websocket.accept()

        if cafe_id not in self.active_connections:
            self.active_connections[cafe_id] = []

        self.active_connections[cafe_id].append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, cafe_id: str, user_id: str):
        if cafe_id in self.active_connections:
            if websocket in self.active_connections[cafe_id]:
                self.active_connections[cafe_id].remove(websocket)

            if not self.active_connections[cafe_id]:
                del self.active_connections[cafe_id]

        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_cafe(self, cafe_id: str, message: dict):
        if cafe_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[cafe_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            for conn in disconnected:
                if conn in self.active_connections[cafe_id]:
                    self.active_connections[cafe_id].remove(conn)

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except Exception:
                del self.user_connections[user_id]


manager = ConnectionManager()

