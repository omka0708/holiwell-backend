from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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
