from typing import Annotated

from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    APIRouter,
    Depends,
    Request)

from starlette.templating import Jinja2Templates

from auth import schema
from chat.utils import ConnectionManager, get_chat_user_by_token

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


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        current_user: Annotated[schema.UserInDB, Depends(get_chat_user_by_token)],
):
    await manager.connect(websocket, current_user.username)
    try:
        while True:
            message = await websocket.receive_json()
            if message['send_to'] == 'all':
                await manager.broadcast(
                    f"Client #{current_user.username} says: {message['text']}",
                    current_user.username)
                await manager.send_personal_message(
                    f"You wrote: {message['text']}",
                    current_user.username)
            else:
                await manager.send_personal_message(
                    f"You wrote: {message['text']}",
                    current_user.username)
                await manager.send_personal_message(
                    f"{current_user.username} wrote to YOU: {message['text']} ",
                    message['send_to'])
    except WebSocketDisconnect:
        manager.disconnect(current_user.username)
        await manager.broadcast(
            f"Client #{current_user.username} left the chat",
            current_user.username)
