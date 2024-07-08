from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Response, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crud, schemas
from app.auth.auth import fastapi_users
from app.auth import schemas, models
from app.lesson import schemas as lesson_schemas
from app.database import get_async_session

router = APIRouter()


@router.get("/all", response_model=list[schemas.UserRead])
async def get_all_users(session: AsyncSession = Depends(get_async_session),
                        user: models.User = Depends(fastapi_users.current_user(superuser=True))):
    return await crud.get_all_users(session)


@router.patch("/update-avatar")
async def update_avatar(avatar: UploadFile = None,
                        user: models.User = Depends(fastapi_users.current_user()),
                        session: AsyncSession = Depends(get_async_session)):
    await crud.update_avatar(user, avatar, session)
    return Response(status_code=204)


@router.post("/plan-lesson", response_model=schemas.PlannedLessonCreate)
async def create_planned_lesson(lesson_id: Annotated[int, Form()],
                                timestamp: Annotated[str, Form()],
                                user: models.User = Depends(fastapi_users.current_user()),
                                session: AsyncSession = Depends(get_async_session)):
    try:
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "msg": f"Field timestamp must have %Y-%m-%dT%H:%M:%S.%f%z format."
        })

    planned_lesson = schemas.PlannedLessonCreate(timestamp=timestamp,
                                                 lesson_id=lesson_id)
    result = await crud.create_planned_lesson(planned_lesson, user.id, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    return Response(status_code=201)


@router.delete("/plan-lesson")
async def delete_link_after_lesson(plan_lesson_id: int,
                                   user: models.User = Depends(fastapi_users.current_user(superuser=True)),
                                   session: AsyncSession = Depends(get_async_session)):
    result = await crud.delete_link_after_lesson(plan_lesson_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Plan lesson {plan_lesson_id} doesn't exist."
        })
    return Response(status_code=204)


@router.get("/my-calendar", response_model=list[schemas.PlannedLessonRead])
async def get_planned_lessons(user: models.User = Depends(fastapi_users.current_user()),
                              session: AsyncSession = Depends(get_async_session)):
    return await crud.get_planned_lessons_by_user(user.id, session)


@router.post("/like-lesson", response_model=schemas.FavoriteCreate)
async def create_favorite(lesson_id: Annotated[int, Form()],
                          user: models.User = Depends(fastapi_users.current_user()),
                          session: AsyncSession = Depends(get_async_session)):
    result = await crud.create_favorite(user.id, lesson_id, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    elif result == 'already_exists':
        raise HTTPException(status_code=409, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} has been already liked."
        })
    return Response(status_code=201)


@router.delete("/like-lesson", response_model=schemas.FavoriteCreate)
async def delete_favorite(lesson_id: Annotated[int, Form()],
                          user: models.User = Depends(fastapi_users.current_user()),
                          session: AsyncSession = Depends(get_async_session)):
    result = await crud.delete_favorite(user.id, lesson_id, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} wasn't liked."
        })
    return Response(status_code=204)


@router.get("/my-favorite", response_model=list[lesson_schemas.LessonRead])
async def get_favorite(user: models.User = Depends(fastapi_users.current_user()),
                       session: AsyncSession = Depends(get_async_session)):
    return await crud.get_favorites_by_user(user.id, session)


@router.post("/watch-lesson", response_model=schemas.ViewCreate)
async def create_view(lesson_id: Annotated[int, Form()],
                      user: models.User = Depends(fastapi_users.current_user()),
                      session: AsyncSession = Depends(get_async_session)):
    result = await crud.create_view(user.id, lesson_id, session)
    if result == 'no_lesson':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} doesn't exist."
        })
    elif result == 'already_exists':
        raise HTTPException(status_code=409, detail={
            "status": "error",
            "msg": f"Lesson {lesson_id} has been already watched."
        })
    return Response(status_code=201)


@router.get("/my-viewed", response_model=list[lesson_schemas.LessonRead])
async def get_views(user: models.User = Depends(fastapi_users.current_user()),
                    session: AsyncSession = Depends(get_async_session)):
    return await crud.get_views_by_user(user.id, session)


router.include_router(
    fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
    tags=["user"],
)
