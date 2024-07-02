from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import fastapi_users
from app.auth.models import User
from app.database import get_async_session
from app.course import schemas, crud

router = APIRouter()


@router.post("/course-type/create", response_model=schemas.CourseTypeCreate)
async def create_course_type(slug: Annotated[str, Form()],
                             user: User = Depends(fastapi_users.current_user(superuser=True)),
                             session: AsyncSession = Depends(get_async_session)):
    course_type = schemas.CourseTypeCreate(slug=slug)
    result = await crud.create_course_type(course_type, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course type {slug} already exist."
        })
    return Response(status_code=201)


@router.get("/course-type/all", response_model=list[schemas.CourseTypeRead])
async def read_course_types(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_course_types(session)


@router.get("/course-type/{course_type_slug}", response_model=schemas.CourseTypeRead)
async def read_course(course_type_slug: str, session: AsyncSession = Depends(get_async_session)):
    result = await crud.get_course_type(course_type_slug, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course type {course_type_slug} doesn't exist."
        })
    return result


@router.post("/create", response_model=schemas.CourseCreate)
async def create_course(title: Annotated[str, Form()],
                        description: Annotated[str, Form()],
                        course_type_id: Annotated[int, Form()],
                        cover: UploadFile = File(...),
                        user: User = Depends(fastapi_users.current_user(superuser=True)),
                        session: AsyncSession = Depends(get_async_session)):
    course = schemas.CourseCreate(title=title,
                                  description=description,
                                  course_type_id=course_type_id)
    result = await crud.create_course(course, cover, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course type {course.course_type_id} doesn't exist."
        })
    return Response(status_code=201)


@router.get("/all", response_model=list[schemas.CourseRead])
async def read_courses(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_courses(session)


@router.get("/{course_id}", response_model=schemas.CourseRead)
async def read_course(course_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await crud.get_course(course_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course {course_id} doesn't exist."
        })
    return result


@router.patch("/{course_id}", response_model=schemas.CourseUpdate)
async def update_course(course_id: int,
                        title: Annotated[str | None, Form()] = None,
                        description: Annotated[str | None, Form()] = None,
                        course_type_id: Annotated[int | None, Form()] = None,
                        cover: UploadFile = None,
                        user: User = Depends(fastapi_users.current_user(superuser=True)),
                        session: AsyncSession = Depends(get_async_session)):
    course = schemas.CourseUpdate(title=title,
                                  description=description,
                                  course_type_id=course_type_id)
    result = await crud.update_course(course_id, course, cover, session)
    if result == 'no_course':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course {course_id} doesn't exist."
        })
    elif result == 'no_course_type':
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course type {course.course_type_id} doesn't exist."
        })
    return Response(status_code=204)


@router.delete("/{course_id}")
async def delete_course(course_id: int,
                        user: User = Depends(fastapi_users.current_user(superuser=True)),
                        session: AsyncSession = Depends(get_async_session)):
    result = await crud.delete_course(course_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course {course_id} doesn't exist."
        })
    return Response(status_code=204)
