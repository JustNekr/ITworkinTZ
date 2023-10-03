from typing import Annotated

from fastapi import (
    Query,
    WebSocketException,
    status,
    Depends,
    WebSocket,
)

from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import get_current_user
from chat.schema import SendMessage
from database import get_async_session


async def get_chat_user_by_token(
        token: Annotated[str | None, Query()] = None,
        session: AsyncSession = Depends(get_async_session),
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    current_user = await get_current_user(token, session)
    return current_user


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.update({username: websocket})

    def disconnect(self, username: str):
        del self.active_connections[username]

    async def send_personal_message(self, message: SendMessage):
        if message.receiver == 'all':
            try:
                await self.active_connections[message.sender].send_json(message.dict())
            except KeyError:
                pass
        else:
            try:
                await self.active_connections[message.receiver].send_json(message.dict())
                await self.active_connections[message.sender].send_json(message.dict())
            except KeyError:
                pass

    async def broadcast(self, message: SendMessage):
        for username, websocket in self.active_connections.items():
            if username != message.sender:
                await websocket.send_json(message.dict())
