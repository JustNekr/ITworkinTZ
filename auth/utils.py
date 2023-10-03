import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, UploadFile
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from auth import schema
from auth import models

from database import get_async_session
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user: schema.UserInDB = await models.User.get_by_username(session, username)
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
        expire = datetime.utcnow() + timedelta(minutes=int(settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        token_data = schema.TokenData(user_id=user_id)
    except JWTError as err:
        print(err)
        raise credentials_exception
    user = await models.User.get_by_id(session, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


async def save_file_to_uploads(file: UploadFile, user_id: int):
    directory = os.path.join(settings.upload_file_path, str(user_id))
    if not os.path.exists(directory):
        os.mkdir(directory)
    full_path = os.path.join(directory, file.filename)
    with open(full_path, "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
    return full_path


def validate_file(file: UploadFile):
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG files allowed")
    max_size = 2 * 1024 * 1024  # 2 MB
    if file.size > max_size:
        raise HTTPException(status_code=400, detail="File size exceeds 2 MB")
    return file
