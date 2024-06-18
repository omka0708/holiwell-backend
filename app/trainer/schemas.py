from pydantic import BaseModel


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


class TrainerUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    description: str | None
