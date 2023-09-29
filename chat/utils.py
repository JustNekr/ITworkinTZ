from typing import Annotated

from fastapi import (
    Query,
    WebSocketException,
    status,
    Depends,
    WebSocket,
)

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth import schema
from auth.utils import get_user
from config import SECRET_KEY, ALGORITHM
from database import get_async_session


async def get_current_chat_user(
        token: str,
        session: AsyncSession
):
    credentials_exception = WebSocketException(code=status.WS_1008_POLICY_VIOLATION)  # TODO: дублирует функцию из auth
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schema.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_chat_user_by_token(
        token: Annotated[str | None, Query()] = None,
        session: AsyncSession = Depends(get_async_session),
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    current_user = get_current_chat_user(token, session)
    return await current_user


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.update({username: websocket})

    def disconnect(self, username: str):
        del self.active_connections[username]

    async def send_personal_message(self, message: str, username: str):
        try:
            await self.active_connections[username].send_text(message)
        except KeyError:
            pass

    async def broadcast(self, message: str, initiator: str):
        for username, websocket in self.active_connections.items():
            if username != initiator:
                await websocket.send_text(message)
