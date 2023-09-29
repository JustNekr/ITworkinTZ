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
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

# DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/postgres"
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
