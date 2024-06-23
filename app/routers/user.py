from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Response, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crud, schemas
from app.auth.auth import fastapi_users
from app.auth.models import User
from app.auth.schemas import UserRead, UserUpdate
from app.database import get_async_session

router = APIRouter()


@router.get("/all")
async def get_all_users(session: AsyncSession = Depends(get_async_session),
                        user: User = Depends(fastapi_users.current_user(superuser=True))):
    return await crud.get_all_users(session)


@router.patch("/update-avatar")
async def update_avatar(avatar: UploadFile = None,
                        user: User = Depends(fastapi_users.current_user()),
                        session: AsyncSession = Depends(get_async_session)):
    await crud.update_avatar(user, avatar, session)
    return Response(status_code=204)


@router.post("/plan-lesson", response_model=schemas.PlannedLessonCreate)
async def create_planned_lesson(lesson_id: Annotated[int, Form()],
                                timestamp: Annotated[str, Form()],
                                user: User = Depends(fastapi_users.current_user()),
                                session: AsyncSession = Depends(get_async_session)):
    try:
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "msg": f"Field timestamp must have Y-m-d H:M:S format."
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
                                   user: User = Depends(fastapi_users.current_user(superuser=True)),
                                   session: AsyncSession = Depends(get_async_session)):
    result = await crud.delete_link_after_lesson(plan_lesson_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Plan lesson {plan_lesson_id} doesn't exist."
        })
    return Response(status_code=204)


@router.get("/my-calendar", response_model=list[schemas.PlannedLessonRead])
async def get_planned_lessons(user: User = Depends(fastapi_users.current_user()),
                              session: AsyncSession = Depends(get_async_session)):
    return await crud.get_planned_lessons_by_user(user.id, session)


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    tags=["user"],
)
