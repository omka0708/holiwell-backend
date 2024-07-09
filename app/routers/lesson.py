from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import fastapi_users
from app.auth.models import User
from app.database import get_async_session
from app.lesson import schemas, crud

router = APIRouter()


@router.post("/create", response_model=schemas.LessonCreate)
async def create_lesson(title: Annotated[str, Form()],
                        description: Annotated[str, Form()],
                        trainer_id: Annotated[int, Form()],
                        course_id: Annotated[int, Form()] = None,
                        cover: UploadFile = File(None),
                        video: UploadFile = File(None),
                        audio: UploadFile = File(None),
                        user: User = Depends(fastapi_users.current_user(superuser=True)),
                        session: AsyncSession = Depends(get_async_session)):
    lesson = schemas.LessonCreate(title=title,
                                  description=description,
                                  trainer_id=trainer_id,
                                  course_id=course_id)
    result = await crud.create_lesson(lesson, cover, video, audio, session)
    if result == 'no_trainer':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Trainer {lesson.trainer_id} doesn't exist."
        })
    return Response(status_code=201)


@router.get("/all", response_model=list[schemas.LessonRead])
async def read_lessons(sort_by: str | None = None,
                       user: User = Depends(fastapi_users.current_user(optional=True)),
                       session: AsyncSession = Depends(get_async_session)):
    sort_by = sort_by.strip().lower() if sort_by is not None else None
    if sort_by is not None and sort_by not in ("new", "popular"):
        raise HTTPException(status_code=422, detail={
            "status": "error",
            "msg": f"Unknown type of sorting ('{sort_by}', but requires 'new' or 'popular')"
        })
    return await crud.get_lessons(sort_by, user.id if user else None, session)


@router.get("/{lesson_id}", response_model=schemas.LessonRead)
async def read_lesson(lesson_id: int,
                      user: User = Depends(fastapi_users.current_user(optional=True)),
                      session: AsyncSession = Depends(get_async_session)):
    result = await crud.get_lesson(lesson_id, user.id if user else None, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    return result


@router.patch("/{lesson_id}", response_model=schemas.LessonUpdate)
async def update_lesson(lesson_id: int,
                        title: Annotated[str | None, Form()] = None,
                        description: Annotated[str | None, Form()] = None,
                        trainer_id: Annotated[int | None, Form()] = None,
                        course_id: Annotated[int | None, Form()] = None,
                        cover: UploadFile = None,
                        video: UploadFile = None,
                        audio: UploadFile = None,
                        user: User = Depends(fastapi_users.current_user(superuser=True)),
                        session: AsyncSession = Depends(get_async_session)):
    lesson = schemas.LessonUpdate(title=title,
                                  description=description,
                                  trainer_id=trainer_id,
                                  course_id=course_id)
    result = await crud.update_lesson(lesson_id, lesson, cover, video, audio, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    elif result == 'no_trainer':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Trainer {lesson.trainer_id} doesn't exist."
        })
    return Response(status_code=204)


@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id: int,
                        user: User = Depends(fastapi_users.current_user(superuser=True)),
                        session: AsyncSession = Depends(get_async_session)):
    result = await crud.delete_lesson(lesson_id, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    return Response(status_code=204)


@router.post("/link-before/create")
async def add_link_before_lesson(lesson_id: int, link_before_lesson_id: int,
                                 user: User = Depends(fastapi_users.current_user(superuser=True)),
                                 session: AsyncSession = Depends(get_async_session)):
    result = await crud.add_link_before_lesson(lesson_id, link_before_lesson_id, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    elif result == 'no_link_before_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {link_before_lesson_id} doesn't exist."
        })
    return Response(status_code=201)


@router.delete("/link-before/{link_before_lesson_id}")
async def delete_link_before_lesson(link_before_lesson_id: int,
                                    user: User = Depends(fastapi_users.current_user(superuser=True)),
                                    session: AsyncSession = Depends(get_async_session)):
    result = await crud.remove_link_before_lesson(link_before_lesson_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Link before lesson {link_before_lesson_id} doesn't exist."
        })
    return Response(status_code=204)


# ===

@router.post("/link-after/create")
async def add_link_after_lesson(lesson_id: int, link_after_lesson_id: int,
                                user: User = Depends(fastapi_users.current_user(superuser=True)),
                                session: AsyncSession = Depends(get_async_session)):
    result = await crud.add_link_after_lesson(lesson_id, link_after_lesson_id, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    elif result == 'no_link_after_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {link_after_lesson_id} doesn't exist."
        })
    return Response(status_code=201)


@router.delete("/link-after/{link_after_lesson_id}")
async def delete_link_after_lesson(link_after_lesson_id: int,
                                   user: User = Depends(fastapi_users.current_user(superuser=True)),
                                   session: AsyncSession = Depends(get_async_session)):
    result = await crud.remove_link_after_lesson(link_after_lesson_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Link after lesson {link_after_lesson_id} doesn't exist."
        })
    return Response(status_code=204)
