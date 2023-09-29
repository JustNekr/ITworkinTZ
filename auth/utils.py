import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, UploadFile
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import schema
from auth import models

# to get a string like this run:
# openssl rand -hex 32
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, UPLOADED_FILES_PATH
from database import get_async_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str):
    query = select(models.User).filter(models.User.username == username)
    result = await session.execute(query)
    return result.scalars().first()


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user: schema.UserInDB = await get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hash_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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


async def create_new_user(
        session: AsyncSession,
        user: schema.UserInDB,
        ):
    user = models.User(**user.__dict__)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
        session: AsyncSession,
        user: schema.UserInDB,
        ):
    user = models.User(**user.__dict__)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def save_file_to_uploads(file: UploadFile, user_id: int):
    print()
    directory = os.path.join(UPLOADED_FILES_PATH, str(user_id))
    if not os.path.exists(directory):
        os.mkdir(directory)
    full_path = os.path.join(directory, file.filename)
    with open(full_path, "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
    return full_path
