from sqlalchemy import Column, Integer, String, ForeignKey, select, DateTime, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, joinedload

from auth import schema as user_schema
from database import Base


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, index=True)

    text = Column(String)

    sender_id = Column(Integer, ForeignKey("user.id"))
    sender = relationship("User", foreign_keys=[sender_id], uselist=False, back_populates="messages")

    receiver_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    receiver = relationship("User", foreign_keys=[receiver_id], uselist=False, back_populates="private_messages")

    posted = Column(DateTime, default=func.now())

    @classmethod
    async def get_chat(
            cls,
            session: AsyncSession,
            user_id: int,
    ):
        query = select(cls).options(joinedload(cls.sender)).options(joinedload(cls.receiver)).filter(or_(
            cls.sender_id == user_id,
            cls.receiver_id.is_(None),
            cls.receiver_id == user_id)).order_by(cls.posted)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def create(
            cls,
            session: AsyncSession,
            text: str,
            sender: user_schema.UserInDB,
            receiver: user_schema.UserInDB,
    ):
        message = cls(text=text, sender=sender, receiver=receiver)
        session.add(message)
        await session.commit()


