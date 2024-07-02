from pydantic import BaseModel, field_serializer, computed_field

from app.config import HOSTNAME
from app.trainer import schemas as trainer_schemas
from app.utils import get_file_length


class LessonCreate(BaseModel):
    title: str
    description: str
    trainer_id: int
    course_id: int | None


class LinkedLessonRead(BaseModel):
    id: int
    lesson_id: int
    linked_lesson_id: int


class LessonRead(BaseModel):
    id: int
    title: str
    description: str
    trainer: trainer_schemas.TrainerRead | None
    course_id: int | None
    path_to_cover: str | None
    path_to_video: str | None
    path_to_audio: str | None
    links_before: list[LinkedLessonRead]
    links_after: list[LinkedLessonRead]

    @computed_field
    @property
    def video_length(self) -> str | None:
        if self.path_to_video is None:
            return
        return get_file_length(self.path_to_video)

    @computed_field
    @property
    def audio_length(self) -> str | None:
        if self.path_to_audio is None:
            return
        return get_file_length(self.path_to_audio)

    @field_serializer('path_to_cover', 'path_to_video', 'path_to_audio')
    def add_hostname(self, path: str | None) -> str | None:
        if type(path) is str:
            return HOSTNAME + path


class LessonUpdate(BaseModel):
    title: str | None
    description: str | None
    trainer_id: int | None
    course_id: int | None
