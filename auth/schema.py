from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    phone_number: str | None = None
    avatar_link: str | None = None
    etc: str | None = None


class NewUser(User):
    password: str | None = None


class UserForDB(User):
    hash_password: str | None = None


class UserInDB(UserForDB):
    id: int | None = None


class UserToUpdate(BaseModel):
    username: str | None = None
    phone_number: str | None = None
    etc: str | None = None
