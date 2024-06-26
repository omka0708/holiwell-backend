from pydantic import BaseModel, field_serializer

from app.config import HOSTNAME


class TrainerCreate(BaseModel):
    first_name: str
    last_name: str
    description: str


class TrainerRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    description: str
    path_to_avatar: str
    path_to_background: str

    @field_serializer('path_to_avatar', 'path_to_background')
    def add_hostname(self, path: str) -> str:
        return HOSTNAME + path


class TrainerUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    description: str | None
