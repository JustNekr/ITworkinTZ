from typing import Annotated

from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    APIRouter,
    Depends,
    Request)
from sqlalchemy.ext.asyncio import AsyncSession

from starlette.templating import Jinja2Templates

from auth.models import User
from auth.schema import UserInDB
from chat.models import Message
from chat.utils import ConnectionManager, get_chat_user_by_token
from database import get_async_session
from chat.schema import ReceiveMessage, SendMessage

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

manager = ConnectionManager()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def get(
        request: Request
):
    return templates.TemplateResponse('chat.html', {'request': request})


@router.get("/all_users")
async def get_all_chat_users():
    users_list = [*manager.active_connections.keys()]
    return {'users_list': users_list}


@router.get("/messages")
async def get_all_chat_messages(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[UserInDB, Depends(get_chat_user_by_token)],
):
    messages = await Message.get_chat(session, current_user.id)
    return {'messages_list': messages}


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        current_user: Annotated[UserInDB, Depends(get_chat_user_by_token)],
):
    await manager.connect(websocket, current_user.username)
    try:
        while True:
            message = ReceiveMessage.parse_obj(await websocket.receive_json())
            receiver = None
            if message.receiver == 'all':
                message_obj = SendMessage(
                    receiver="all",
                    text=message.text,
                    sender=current_user.username
                )
                await manager.broadcast(message_obj)
                await manager.send_personal_message(message_obj)
            else:

                receiver = await User.get_by_username(session, message.receiver)
                message_obj = SendMessage(
                    receiver=message.receiver,
                    text=message.text,
                    sender=current_user.username
                )
                await manager.send_personal_message(message_obj)

            await Message.create(
                session=session,
                text=message.text,
                sender=current_user,
                receiver=receiver)

    except WebSocketDisconnect:
        manager.disconnect(current_user.username)
        message_dict = SendMessage(
            receiver="all",
            text='left the chat',
            sender=current_user.username
        )
        await manager.broadcast(message_dict)
