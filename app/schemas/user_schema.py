from pydantic import BaseModel, EmailStr

from app.common.constants import UserType


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    type: UserType


class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    type: UserType

    model_config = {"from_attributes": True}


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
