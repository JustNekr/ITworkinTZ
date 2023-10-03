# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# from config.config import settings
#
# SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
#
# if 'sqlite://' in SQLALCHEMY_DATABASE_URL:
#     engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
# else:
#     engine = create_engine(SQLALCHEMY_DATABASE_URL)
#
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
#
# Base = declarative_base()
from typing import AsyncGenerator

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from config import settings


DATABASE_URL = f"{settings.db_engine}://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
