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
    result = await crud.create_course_type(course_type, user.id if user else None, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Course type {slug} already exist."
        })
    return Response(status_code=201)


@router.get("/course-type/all", response_model=list[schemas.CourseTypeRead])
async def read_course_types(sort_by: str | None = None,
                            user: User = Depends(fastapi_users.current_user(optional=True)),
                            session: AsyncSession = Depends(get_async_session)):
    sort_by = sort_by.strip().lower() if sort_by is not None else None
    if sort_by is not None and sort_by not in ("new", "popular"):
        raise HTTPException(status_code=422, detail={
            "status": "error",
            "msg": f"Unknown type of sorting ('{sort_by}', but requires 'new' or 'popular')"
        })
    return await crud.get_course_types(user.id if user else None, sort_by, session)


@router.get("/course-type/{course_type_slug}", response_model=schemas.CourseTypeRead)
async def read_course(course_type_slug: str,
                      sort_by: str | None = None,
                      user: User = Depends(fastapi_users.current_user(optional=True)),
                      session: AsyncSession = Depends(get_async_session)):
    sort_by = sort_by.strip().lower() if sort_by is not None else None
    if sort_by is not None and sort_by not in ("new", "popular"):
        raise HTTPException(status_code=422, detail={
            "status": "error",
            "msg": f"Unknown type of sorting ('{sort_by}', but requires 'new' or 'popular')"
        })

    result = await crud.get_course_type(course_type_slug, user.id if user else None, sort_by, session)
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
async def read_courses(sort_by: str | None = None,
                       user: User = Depends(fastapi_users.current_user(optional=True)),
                       session: AsyncSession = Depends(get_async_session)):
    sort_by = sort_by.strip().lower() if sort_by is not None else None
    if sort_by is not None and sort_by not in ("new", "popular"):
        raise HTTPException(status_code=422, detail={
            "status": "error",
            "msg": f"Unknown type of sorting ('{sort_by}', but requires 'new' or 'popular')"
        })
    return await crud.get_courses(user.id if user else None, sort_by, session)


@router.get("/{course_id}", response_model=schemas.CourseRead)
async def read_course(course_id: int, sort_by: str | None = None,
                      user: User = Depends(fastapi_users.current_user(optional=True)),
                      session: AsyncSession = Depends(get_async_session)):
    sort_by = sort_by.strip().lower() if sort_by is not None else None
    if sort_by is not None and sort_by not in ("new", "popular"):
        raise HTTPException(status_code=422, detail={
            "status": "error",
            "msg": f"Unknown type of sorting ('{sort_by}', but requires 'new' or 'popular')"
        })

    result = await crud.get_course(course_id, user.id if user else None, sort_by, session)
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
