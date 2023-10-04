from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from auth import schema
from auth.utils import get_password_hash
from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hash_password = Column(String)
    avatar_link = Column(String)
    phone_number = Column(String)
    etc = Column(String)

    messages = relationship("Message", back_populates="sender", foreign_keys='Message.sender_id')
    private_messages = relationship("Message", back_populates="receiver", foreign_keys='Message.receiver_id')

    @classmethod
    async def get_by_username(
            cls,
            session: AsyncSession,
            username: str
    ):
        query = select(cls).filter(cls.username == username)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_id(
            cls,
            session: AsyncSession,
            user_id: int
    ):
        query = select(cls).filter(cls.id == user_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def create(
            cls,
            session: AsyncSession,
            user: schema.NewUser,
    ):
        user = schema.UserForDB(
            username=user.username,
            phone_number=user.phone_number,
            etc=user.etc,
            hash_password=get_password_hash(user.password)
        )
        user_from_db = await cls.get_by_username(session, user.username)
        if not user_from_db:
            user = cls(**user.__dict__)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        else:
            return False

    @classmethod
    async def get_matching_users(
            cls,
            session: AsyncSession,
            query: str,
    ):
        db_query = select(cls).filter(cls.username.ilike(f"%{query}%"))
        result = await session.execute(db_query)
        return result.scalars().all()

    async def update(
            self,
            session: AsyncSession,
            user_to_update: schema.UserToUpdate,
    ):
        for key, value in user_to_update.__dict__.items():
            if value:
                setattr(self, key, value)
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

    async def add_avatar_link(
            self,
            session: AsyncSession,
            avatar_link: str,
    ):
        self.avatar_link = avatar_link
        await session.commit()
        await session.refresh(self)
        return self
