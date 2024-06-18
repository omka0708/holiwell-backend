from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    path_to_avatar: str | None

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None


class EmailSchema(BaseModel):
    email: list[EmailStr]
