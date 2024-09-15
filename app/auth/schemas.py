from datetime import datetime
from typing import Any

from click import password_option
from typing_extensions import Self

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_serializer, model_validator, model_serializer

from app.config import HOSTNAME
from app.lesson import schemas as lesson_schemas


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    email: str | None
    tg_id: int | None
    path_to_avatar: str | None
    is_superuser: bool

    @field_serializer('path_to_avatar')
    def add_hostname(self, path: str) -> str | None:
        if path:
            return HOSTNAME + path

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    tg_id: int | None = None
    email: EmailStr | None = None

    @model_validator(mode='after')
    def validate_email_and_tg_id(self):
        if self.email is None and self.tg_id is None:
            raise ValueError("User must have email or tg_id")
        return self


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None


class EmailSchema(BaseModel):
    email: list[EmailStr]


class PlannedLessonCreate(BaseModel):
    timestamp: datetime
    lesson_id: int


class PlannedLessonRead(BaseModel):
    id: int
    timestamp: datetime
    lesson: lesson_schemas.LessonRead


class FavoriteCreate(BaseModel):
    lesson_id: int


class ViewCreate(BaseModel):
    lesson_id: int
