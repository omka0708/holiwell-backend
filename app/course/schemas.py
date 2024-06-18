from pydantic import BaseModel

from app.lesson import schemas as lesson_schemas


class CourseCreate(BaseModel):
    title: str
    description: str
    course_type_id: int | None


class CourseRead(BaseModel):
    id: int
    title: str
    description: str
    path_to_cover: str | None
    lessons: list[lesson_schemas.LessonRead]


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
