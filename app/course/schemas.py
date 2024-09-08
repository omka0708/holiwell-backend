from pydantic import BaseModel, field_serializer

from app.config import HOSTNAME
from app.lesson import schemas as lesson_schemas


class CourseCreate(BaseModel):
    title: str
    description: str
    course_type_id: int | None


class CourseRead(BaseModel):
    id: int
    title: str
    description: str
    course_type_id: int | None
    course_type_slug: str | None
    path_to_cover: str | None
    number_of_views: int
    lessons: list[lesson_schemas.LessonRead]

    @field_serializer('path_to_cover')
    def add_hostname(self, path: str) -> str:
        return HOSTNAME + path


class CourseUpdate(BaseModel):
    title: str | None
    description: str | None
    course_type_id: int | None


class CourseTypeCreate(BaseModel):
    slug: str


class CourseTypeRead(BaseModel):
    id: int
    slug: str
    courses: list[CourseRead]
