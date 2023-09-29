from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hash_password = Column(String)
    avatar_link = Column(String)
    phone_number = Column(String)
    etc = Column(String)

