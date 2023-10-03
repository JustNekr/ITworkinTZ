from typing import Annotated, Union, Optional

from pydantic import BaseModel
from fastapi.param_functions import Form


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Union[int, None] = None


class User(BaseModel):
    username: Annotated[str, Form()]
    phone_number: Annotated[Union[str, None], Form()] = None
    etc: Annotated[Union[str, None], Form()] = None


class NewUser(User):
    password: Annotated[str, Form()]


class UserForDB(User):
    hash_password: Annotated[str, Form()]


class UserInDB(UserForDB):
    id: int


class UserFromDB(UserInDB):
    avatar_link: str


class UserToUpdate(BaseModel):
    username: Annotated[Optional[Union[str, None]], Form()] = None
    phone_number: Annotated[Union[str, None], Form()] = None
    etc: Annotated[Union[str, None], Form()] = None
