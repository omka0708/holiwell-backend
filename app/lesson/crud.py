from fastapi import UploadFile
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.lesson import models, schemas
from app.auth import models as auth_models
from app.trainer import models as trainer_models
from app.trainer.crud import get_trainer
from app.utils import upload_file, delete_file


async def create_lesson(lesson: schemas.LessonCreate,
                        cover: UploadFile | None,
                        video: UploadFile | None,
                        audio: UploadFile | None,
                        db: AsyncSession):
    lesson_dict = lesson.model_dump()
    db_trainer = await db.get(trainer_models.Trainer, lesson_dict['trainer_id'])
    if not db_trainer:
        return 'no_trainer'

    lesson_dict['path_to_cover'] = upload_file('lessons/cover', cover, cover.filename) if cover else None
    lesson_dict['path_to_video'] = upload_file('lessons/video', video, video.filename) if video else None
    lesson_dict['path_to_audio'] = upload_file('lessons/audio', audio, audio.filename) if audio else None

    db_lesson = models.Lesson(**lesson_dict)
    db.add(db_lesson)

    await db.commit()
    return db_lesson


async def get_lesson(lesson_id: int, user_id: int | None, db: AsyncSession):
    db_lesson = await db.get(models.Lesson, lesson_id)
    if not db_lesson:
        return

    db_lesson.course_type_slug = db_lesson.course.course_type.slug if db_lesson.course is not None else None
    db_lesson.trainer = await get_trainer(db_lesson.trainer_id, db)
    db_lesson.links_before = await get_links_before_by_lesson(lesson_id, db)
    db_lesson.links_after = await get_links_after_by_lesson(lesson_id, db)
    db_lesson.number_of_views = await get_number_of_views(lesson_id, db)
    db_lesson.is_viewed = await is_viewed(lesson_id, user_id, db)
    db_lesson.is_favorite = await is_favorite(lesson_id, user_id, db)

    return db_lesson


async def get_lessons(sort_by: str | None, user_id: int | None, course_type_slug: str | None, db: AsyncSession):
    db_lessons = await db.execute(select(models.Lesson))
    obj_lessons = db_lessons.scalars().all()

    for obj in obj_lessons:
        obj.course_type_slug = obj.course.course_type.slug if obj.course is not None else None
        obj.trainer = await get_trainer(obj.trainer_id, db)
        obj.links_before = await get_links_before_by_lesson(obj.id, db)
        obj.links_after = await get_links_after_by_lesson(obj.id, db)
        obj.number_of_views = await get_number_of_views(obj.id, db)
        obj.is_viewed = await is_viewed(obj.id, user_id, db)
        obj.is_favorite = await is_favorite(obj.id, user_id, db)

    if sort_by is None or sort_by == "new":
        obj_lessons = sorted(obj_lessons, key=lambda x: -x.id)
    elif sort_by == "popular":
        obj_lessons = sorted(obj_lessons, key=lambda x: -x.number_of_views)

    if course_type_slug:
        obj_lessons = list(filter(lambda x: x.course_type_slug == course_type_slug, obj_lessons))
    return obj_lessons


async def update_lesson(lesson_id: int,
                        lesson: schemas.LessonUpdate,
                        cover: UploadFile,
                        video: UploadFile,
                        audio: UploadFile,
                        db: AsyncSession):
    db_lesson = await db.get(models.Lesson, lesson_id)
    if not db_lesson:
        return 'no_lesson'

    lesson_dict = lesson.model_dump(exclude_none=True)
    if 'trainer_id' in lesson_dict:
        db_trainer = await db.get(trainer_models.Trainer, lesson_dict['trainer_id'])
        if not db_trainer:
            return 'no_trainer'

    if cover:
        if db_lesson.path_to_cover:
            delete_file(db_lesson.path_to_cover)
        lesson_dict['path_to_cover'] = upload_file('lessons/cover', cover, cover.filename)
    if video:
        if db_lesson.path_to_video:
            delete_file(db_lesson.path_to_video)
        lesson_dict['path_to_video'] = upload_file('lessons/video', video, video.filename)
    if audio:
        if db_lesson.path_to_audio:
            delete_file(db_lesson.path_to_audio)
        lesson_dict['path_to_audio'] = upload_file('lessons/audio', audio, audio.filename)

    for key, value in lesson_dict.items():
        setattr(db_lesson, key, value)

    await db.commit()
    return db_lesson


async def delete_lesson(lesson_id: int, db: AsyncSession):
    db_lesson = await db.get(models.Lesson, lesson_id)
    if not db_lesson:
        return 'no_lesson'

    try:
        delete_file(db_lesson.path_to_cover)
        delete_file(db_lesson.path_to_video)
        delete_file(db_lesson.path_to_audio)
    except FileNotFoundError:
        pass

    await db.delete(db_lesson)
    await db.commit()


async def add_link_before_lesson(lesson_id: int,
                                 link_before_lesson_id: int,
                                 db: AsyncSession):
    db_lesson = await db.get(models.Lesson, lesson_id)
    if not db_lesson:
        return 'no_lesson'

    db_lesson = await db.get(models.Lesson, link_before_lesson_id)
    if not db_lesson:
        return 'no_link_before_lesson'

    db_link_before_lesson = models.LinkBeforeLesson(lesson_id=lesson_id, linked_lesson_id=link_before_lesson_id)
    db.add(db_link_before_lesson)

    await db.commit()
    return db_lesson


async def remove_link_before_lesson(link_before_lesson_id: int,
                                    db: AsyncSession):
    db_link_before_lesson = await db.get(models.LinkBeforeLesson, link_before_lesson_id)
    if not db_link_before_lesson:
        return
    await db.delete(db_link_before_lesson)
    await db.commit()
    return True


async def get_links_before_by_lesson(lesson_id: int, db: AsyncSession):
    db_link_before_lesson = await db.execute(select(models.LinkBeforeLesson).
                                             where(models.LinkBeforeLesson.lesson_id == lesson_id))
    obj_link_before_lesson = db_link_before_lesson.scalars().all()
    # result = [item.__dict__['linked_lesson_id'] for item in obj_link_before_lesson]
    return obj_link_before_lesson


# ===

async def add_link_after_lesson(lesson_id: int,
                                link_after_lesson_id: int,
                                db: AsyncSession):
    db_lesson = await db.get(models.Lesson, lesson_id)
    if not db_lesson:
        return 'no_lesson'

    db_lesson = await db.get(models.Lesson, link_after_lesson_id)
    if not db_lesson:
        return 'no_link_after_lesson'

    db_link_after_lesson = models.LinkAfterLesson(lesson_id=lesson_id, linked_lesson_id=link_after_lesson_id)
    db.add(db_link_after_lesson)

    await db.commit()
    return db_lesson


async def remove_link_after_lesson(link_after_lesson_id: int,
                                   db: AsyncSession):
    db_link_after_lesson = await db.get(models.LinkAfterLesson, link_after_lesson_id)
    if not db_link_after_lesson:
        return
    await db.delete(db_link_after_lesson)
    await db.commit()
    return True


async def get_links_after_by_lesson(lesson_id: int, db: AsyncSession):
    db_link_after_lesson = await db.execute(select(models.LinkAfterLesson).
                                            where(models.LinkAfterLesson.lesson_id == lesson_id))
    obj_link_after_lesson = db_link_after_lesson.scalars().all()
    return obj_link_after_lesson


async def get_number_of_views(lesson_id: int, db: AsyncSession) -> int:
    cnt = await db.execute(select(func.count()).select_from(auth_models.View).
                           where(auth_models.View.lesson_id == lesson_id))
    return cnt.scalar()


async def is_viewed(lesson_id: int, user_id: int | None, db: AsyncSession) -> bool:
    if user_id is None:
        return False
    cnt = await db.execute(select(func.count()).select_from(auth_models.View).
                           where(and_(auth_models.View.lesson_id == lesson_id,
                                      auth_models.View.user_id == user_id)))
    return cnt.scalar() > 0


async def is_favorite(lesson_id: int, user_id: int | None, db: AsyncSession) -> bool:
    if user_id is None:
        return False
    cnt = await db.execute(select(func.count()).select_from(auth_models.Favorite).
                           where(and_(auth_models.Favorite.lesson_id == lesson_id,
                                      auth_models.Favorite.user_id == user_id)))
    return cnt.scalar() > 0
