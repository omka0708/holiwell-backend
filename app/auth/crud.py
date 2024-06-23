from datetime import datetime

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import models, schemas
from app.lesson import models as lesson_models
from app.lesson.crud import get_lesson
from app.auth.models import User
from app.utils import delete_file, upload_file


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()[:1000]
    return users


async def update_avatar(user: User, avatar: UploadFile, db: AsyncSession):
    delete_file(user.path_to_avatar)
    user.path_to_avatar = upload_file('users/avatar', avatar, avatar.filename if avatar else None)
    await db.commit()


async def create_planned_lesson(planned_lesson: schemas.PlannedLessonCreate, user_id: int, db: AsyncSession):
    db_lesson = await db.get(lesson_models.Lesson, planned_lesson.lesson_id)
    if not db_lesson:
        return 'no_lesson'

    planned_lesson_dict = planned_lesson.model_dump()
    planned_lesson_dict['user_id'] = user_id

    db_planned_lesson = models.PlannedLesson(**planned_lesson_dict)
    db.add(db_planned_lesson)

    await db.commit()
    return db_lesson


async def get_planned_lessons_by_user(user_id: int, db: AsyncSession):
    db_planned_lessons = await db.execute(select(models.PlannedLesson).
                                          where(models.PlannedLesson.user_id == user_id))
    obj_planned_lessons = db_planned_lessons.scalars().all()

    for obj in obj_planned_lessons:
        obj.lesson = await get_lesson(obj.lesson_id, db)

    return obj_planned_lessons
