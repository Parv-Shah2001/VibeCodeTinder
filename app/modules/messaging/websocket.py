"""
WebSocket manager for real-time messaging.
Scale design:
- In single monolith, in-memory dict holds connections.
- For horizontal scale (multiple pods), use Redis Pub/Sub to broadcast.
- Each user may have multiple devices.
- For 200M messages/day, we need connection pooling, heartbeat, and offline queue (push notification fallback).
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
import structlog

logger = structlog.get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}  # user_id -> list of websockets
        self.typing_state: Dict[int, Dict[int, bool]] = {}  # conversation_id -> user_id -> is_typing

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info("ws_connected", user_id=user_id, total=len(self.active_connections[user_id]))

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info("ws_disconnected", user_id=user_id)

    async def send_personal_message(self, user_id: int, message: dict):
        # Send to all sockets of user
        connections = self.active_connections.get(user_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

        # For horizontal scaling, publish to redis
        try:
            from app.core.redis import redis_client
            redis_client.publish(f"ws:user:{user_id}", json.dumps(message))
        except Exception:
            pass

    async def broadcast_to_conversation(self, conversation_id: int, user1_id: int, user2_id: int, message: dict):
        # Send to both participants if online
        await self.send_personal_message(user1_id, message)
        await self.send_personal_message(user2_id, message)

    async def send_typing_indicator(self, conversation_id: int, sender_id: int, receiver_id: int, is_typing: bool):
        await self.send_personal_message(receiver_id, {
            "type": "typing",
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "is_typing": is_typing,
        })

manager = ConnectionManager()

# Redis subscriber for cross-instance ws broadcast would run in background task.
# Simplified version omitted for brevity but architecture allows it.
