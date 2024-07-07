from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import models, schemas
from app.auth.models import User
from app.lesson import models as lesson_models
from app.lesson.crud import get_lesson
from app.utils import delete_file, upload_file


async def get_all_users(db: AsyncSession):
    db_users = await db.execute(select(User))
    obj_users = db_users.scalars().all()
    return obj_users


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


async def delete_link_after_lesson(plan_lesson_id: int, db: AsyncSession):
    db_link_after_lesson = await db.get(models.PlannedLesson, plan_lesson_id)
    if not db_link_after_lesson:
        return

    await db.delete(db_link_after_lesson)
    await db.commit()
    return True


async def get_planned_lessons_by_user(user_id: int, db: AsyncSession):
    db_planned_lessons = await db.execute(select(models.PlannedLesson).where(models.PlannedLesson.user_id == user_id))
    obj_planned_lessons = db_planned_lessons.scalars().all()

    for obj in obj_planned_lessons:
        obj.lesson = await get_lesson(obj.lesson_id, db)

    return obj_planned_lessons


async def create_view(user_id: int, lesson_id: int, db: AsyncSession):
    db_lesson = await db.get(lesson_models.Lesson, lesson_id)
    if not db_lesson:
        return 'no_lesson'

    db_view = models.View(
        **{
            'user_id': user_id,
            'lesson_id': lesson_id
        }
    )
    db.add(db_view)

    await db.commit()
    return db_view


async def create_favorite(user_id: int, lesson_id: int, db: AsyncSession):
    db_lesson = await db.get(lesson_models.Lesson, lesson_id)
    if not db_lesson:
        return 'no_lesson'

    db_lesson = await db.execute(select(models.Favorite).where(
        models.Favorite.user_id == user_id and models.Favorite.lesson_id == lesson_id))
    if db_lesson:
        return 'already_exists'

    db_favorite = models.Favorite(
        **{
            'user_id': user_id,
            'lesson_id': lesson_id
        }
    )
    db.add(db_favorite)

    await db.commit()
    return db_favorite


async def get_views_by_user(user_id: int, db: AsyncSession):
    db_views = await db.execute(select(models.View).where(models.View.user_id == user_id))
    lesson_ids = tuple(view.lesson_id for view in db_views.scalars().all())
    if not lesson_ids:
        return []
    obj_lessons = [await get_lesson(lesson_id, db) for lesson_id in lesson_ids]
    return obj_lessons


async def get_favorites_by_user(user_id: int, db: AsyncSession):
    db_favorites = await db.execute(select(models.Favorite).where(models.Favorite.user_id == user_id))
    lesson_ids = tuple(view.lesson_id for view in db_favorites.scalars().all())
    if not lesson_ids:
        return []
    obj_lessons = [await get_lesson(lesson_id, db) for lesson_id in lesson_ids]
    return obj_lessons


async def delete_favorite(lesson_id: int, db: AsyncSession):
    db_lesson = await db.get(lesson_models.Lesson, lesson_id)
    if not db_lesson:
        return 'no_lesson'

    await db.delete(db_lesson)
    await db.commit()
