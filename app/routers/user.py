from fastapi import APIRouter, Depends, UploadFile, Response
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


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    tags=["user"],
)
