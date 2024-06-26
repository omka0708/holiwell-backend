from datetime import datetime

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_serializer

from app.config import HOSTNAME
from app.lesson import schemas as lesson_schemas


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    path_to_avatar: str | None

    @field_serializer('path_to_avatar')
    def add_hostname(self, path: str) -> str:
        return HOSTNAME + path

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


class PlannedLessonCreate(BaseModel):
    timestamp: datetime
    lesson_id: int


class PlannedLessonRead(BaseModel):
    id: int
    timestamp: datetime
    lesson: lesson_schemas.LessonRead
