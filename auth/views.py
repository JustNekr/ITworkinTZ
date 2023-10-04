import os
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, Body, HTTPException, UploadFile, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth import schema
from auth.models import User
from auth.utils import authenticate_user, create_access_token, get_current_user, \
    save_file_to_uploads, validate_file
from config import settings
from database import get_async_session

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/token", response_model=schema.Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_async_session)

):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=int(settings.access_token_expire_minutes))
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user", response_model=schema.UserFromDB)
async def get_self_user(
    current_user: Annotated[schema.UserFromDB, Depends(get_current_user)]
):
    return current_user


@router.post("/user", response_model=schema.UserInDB | dict)
async def create_user(
        user: Annotated[schema.NewUser, Depends()],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        response: Response
):
    user = await User.create(session, user)
    if user:
        return user
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {'msg': 'already exist'}


@router.put("/user", response_model=schema.UserInDB)
async def update_user(
        current_user: Annotated[schema.UserInDB, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user_to_update: Annotated[schema.UserToUpdate, Depends()],
):
    return await current_user.update(session, user_to_update)


@router.get("/users/search")
async def search_users(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        query: str = Query(None, title="Query", description="Search query"),
):
    if not query:
        return {"msg": "provide a query parameter"}
    matching_users = await User.get_matching_users(session, query)
    return {"users": matching_users}


@router.post("/user/avatar", response_model=schema.UserFromDB)
async def add_avatar(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        avatar: Annotated[UploadFile, Depends(validate_file)]
):
    avatar_path = None
    if avatar:
        avatar_path: str = await save_file_to_uploads(avatar, current_user.id)
    return await current_user.add_avatar_link(session, avatar_path)

