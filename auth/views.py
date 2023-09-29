import os
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, Body, HTTPException, UploadFile, File
from fastapi.openapi.models import Schema
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth import schema
from auth.utils import authenticate_user, create_access_token, get_current_user, get_password_hash, create_new_user, \
    save_file_to_uploads
from config import ACCESS_TOKEN_EXPIRE_MINUTES, UPLOADED_FILES_PATH
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
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=schema.UserInDB)
async def read_users_me(
    current_user: Annotated[schema.UserInDB, Depends(get_current_user)]
):
    return current_user


@router.post("/create_user", response_model=schema.UserInDB)
async def create_user(
        user: Annotated[schema.NewUser, Body()],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    user = schema.UserForDB(
        username=user.username,
        avatar_link=user.avatar_link,
        phone_number=user.avatar_link,
        etc=user.etc,
        hash_password=get_password_hash(user.password)
    )
    user = await create_new_user(session, user)
    return user


@router.post("/update_user", response_model=schema.UserInDB)
async def update_user(
        current_user: Annotated[schema.UserInDB, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        username: Annotated[str | None, Body()] = None,
        phone_number: Annotated[str | None, Body()] = None,
        etc: Annotated[str | None, Body()] = None,

):
    current_user.username = username if username else current_user.username
    current_user.phone_number = phone_number if phone_number else current_user.phone_number
    current_user.etc = etc if etc else current_user.etc
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.post("/avatar", response_model=schema.UserInDB)
async def add_avatar(
        current_user: Annotated[schema.UserInDB, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
        avatar: UploadFile = File(...),
):
    avatar_path = None
    if avatar:
        avatar_path: str = await save_file_to_uploads(avatar, current_user.id)
    current_user.avatar_link = avatar_path
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user
