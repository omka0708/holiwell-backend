from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.course import models, schemas
from app.lesson import models as lesson_models
from app.lesson.crud import (get_links_before_by_lesson, get_links_after_by_lesson, get_number_of_views,
                             is_viewed, is_favorite)
from app.utils import upload_file, delete_file


async def create_course_type(course_type: schemas.CourseTypeCreate, user_id: int | None, db: AsyncSession):
    course_type_dict = course_type.model_dump()
    db_course_type = models.CourseType(**course_type_dict)
    db_course_types = await get_course_types(user_id, None, db)

    db_course_types_slugs = [item.slug for item in db_course_types]
    if db_course_type.slug in db_course_types_slugs:
        return

    db.add(db_course_type)

    await db.commit()
    return db_course_type


async def get_course_types(user_id: int | None, sort_by: str | None, db: AsyncSession):
    db_course_type = await db.execute(select(models.CourseType).limit(1000))
    obj_course_types = db_course_type.scalars().all()

    for obj_course_type in obj_course_types:
        for course in obj_course_type.courses:
            course.course_type_slug = obj_course_type.slug
            course.course_type_id = obj_course_type.id
            course.number_of_views = 0

            for lesson in course.lessons:
                lesson.links_before = await get_links_before_by_lesson(lesson.id, db)
                lesson.links_after = await get_links_after_by_lesson(lesson.id, db)
                lesson.course_type_slug = obj_course_type.slug
                lesson.number_of_views = await get_number_of_views(lesson.id, db)
                lesson.is_viewed = await is_viewed(lesson.id, user_id, db)
                lesson.is_favorite = await is_favorite(lesson.id, user_id, db)
                course.number_of_views += lesson.number_of_views

            if sort_by is None or sort_by == "new":
                course.lessons = sorted(course.lessons, key=lambda x: -x.id)
            elif sort_by == "popular":
                course.lessons = sorted(course.lessons, key=lambda x: -x.number_of_views)

    return sorted(obj_course_types, key=lambda x: x.id)


async def get_course_type(course_type_slug: str, user_id: int | None, sort_by: str | None, db: AsyncSession):
    db_course_type = await db.execute(select(models.CourseType).where(models.CourseType.slug == course_type_slug))
    obj_course_type = db_course_type.scalar()
    if not obj_course_type:
        return

    for course in obj_course_type.courses:
        course.course_type_slug = obj_course_type.slug
        course.course_type_id = obj_course_type.id
        course.number_of_views = 0

        for lesson in course.lessons:
            lesson.links_before = await get_links_before_by_lesson(lesson.id, db)
            lesson.links_after = await get_links_after_by_lesson(lesson.id, db)
            lesson.course_type_slug = obj_course_type.slug
            lesson.number_of_views = await get_number_of_views(lesson.id, db)
            lesson.is_viewed = await is_viewed(lesson.id, user_id, db)
            lesson.is_favorite = await is_favorite(lesson.id, user_id, db)
            course.number_of_views += lesson.number_of_views

        if sort_by is None or sort_by == "new":
            course.lessons = sorted(course.lessons, key=lambda x: -x.id)
        elif sort_by == "popular":
            course.lessons = sorted(course.lessons, key=lambda x: -x.number_of_views)

    return obj_course_type


async def create_course(course: schemas.CourseCreate,
                        cover: UploadFile,
                        db: AsyncSession):
    course_dict = course.model_dump()
    db_course_type = await db.get(models.CourseType, course_dict['course_type_id'])
    if not db_course_type:
        return

    course_dict['path_to_cover'] = upload_file('courses/cover', cover, cover.filename)
    db_course = models.Course(**course_dict)
    db.add(db_course)

    await db.commit()
    return db_course


async def get_lessons_by_course(course_id: int, db: AsyncSession):
    db_lessons = await db.execute(select(lesson_models.Lesson).where(lesson_models.Lesson.course_id == course_id))
    obj_lessons = db_lessons.scalars().all()
    return obj_lessons


async def get_course(course_id: int, user_id: int | None, sort_by: str | None, db: AsyncSession):
    db_course = await db.get(models.Course, course_id)
    if not db_course:
        return

    db_course.course_type_slug = db_course.course_type.slug
    db_course.course_type_id = db_course.course_type.id
    db_course.number_of_views = 0
    for lesson in db_course.lessons:
        lesson.course_type_slug = db_course.course_type.slug
        lesson.links_before = await get_links_before_by_lesson(lesson.id, db)
        lesson.links_after = await get_links_after_by_lesson(lesson.id, db)
        lesson.course_type_slug = lesson.course.course_type.slug if lesson.course is not None else None
        lesson.number_of_views = await get_number_of_views(lesson.id, db)
        lesson.is_viewed = await is_viewed(lesson.id, user_id, db)
        lesson.is_favorite = await is_favorite(lesson.id, user_id, db)
        db_course.number_of_views += lesson.number_of_views

    if sort_by is None or sort_by == "new":
        db_course.lessons = sorted(db_course.lessons, key=lambda x: -x.id)
    elif sort_by == "popular":
        db_course.lessons = sorted(db_course.lessons, key=lambda x: -x.number_of_views)

    return db_course


async def get_courses(user_id: int | None, sort_by: str | None, db: AsyncSession):
    db_courses = await db.execute(select(models.Course).limit(1000))
    obj_courses = db_courses.scalars().all()

    for obj in obj_courses:
        obj.course_type_slug = obj.course_type.slug
        obj.course_type_id = obj.course_type.id
        obj.number_of_views = 0
        for lesson in obj.lessons:
            lesson.course_type_slug = obj.course_type.slug
            lesson.links_before = await get_links_before_by_lesson(lesson.id, db)
            lesson.links_after = await get_links_after_by_lesson(lesson.id, db)
            lesson.course_type_slug = obj.course_type.slug
            lesson.number_of_views = await get_number_of_views(lesson.id, db)
            lesson.is_viewed = await is_viewed(lesson.id, user_id, db)
            lesson.is_favorite = await is_favorite(lesson.id, user_id, db)
            obj.number_of_views += lesson.number_of_views

    if sort_by is None or sort_by == "new":
        obj_courses = sorted(obj_courses, key=lambda x: -x.id)
    elif sort_by == "popular":
        obj_courses = sorted(obj_courses, key=lambda x: -x.number_of_views)

    return obj_courses


async def update_course(course_id: int,
                        course: schemas.CourseUpdate,
                        cover: UploadFile,
                        db: AsyncSession):
    db_course = await db.get(models.Course, course_id)
    if not db_course:
        return 'no_course'

    course_dict = course.model_dump(exclude_none=True)
    if 'course_type_id' in course_dict:
        db_course_type = await db.get(models.CourseType, course_dict['course_type_id'])
        if not db_course_type:
            return 'no_course_type'

    if cover:
        if db_course.path_to_cover:
            delete_file(db_course.path_to_cover)
        course_dict['path_to_cover'] = upload_file('courses/cover', cover, cover.filename)

    for key, value in course_dict.items():
        setattr(db_course, key, value)

    await db.commit()
    return db_course


async def delete_course(course_id: int, db: AsyncSession):
    db_lesson = await db.get(models.Course, course_id)
    if not db_lesson:
        return

    try:
        delete_file(db_lesson.path_to_cover)
    except FileNotFoundError:
        pass

    await db.delete(db_lesson)
    await db.commit()
    return True
