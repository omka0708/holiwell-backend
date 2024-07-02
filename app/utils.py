import shutil
import os
import shortuuid

from pymediainfo import MediaInfo
from fastapi import Depends, UploadFile
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.database import get_async_session


# SERVER_IP = f"http://{requests.get('https://httpbin.org/ip').json()['origin']}"


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


def get_unique_short_uuid4() -> str:
    return shortuuid.uuid()


def upload_file(path: str, file: UploadFile, filename: str) -> str | None:
    if not file or not filename:
        return None

    path_model, path_field = path.split('/')
    if path_model not in os.listdir("files"):
        os.mkdir(f"files/{path_model}")
        os.mkdir(f"files/{path_model}/{path_field}")

    unique_name = str(get_unique_short_uuid4())
    os.mkdir(f"files/{path}/{unique_name}")
    location = f"files/{path}/{unique_name}/{filename}"

    with open(location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    return location


def delete_file(path: str):
    if path:
        directory = '/'.join(path.split('/')[:-1])
        os.remove(path)
        if not os.listdir(directory):
            os.rmdir(directory)


def get_file_length(path: str) -> str | None:
    if path:
        try:
            media_info = MediaInfo.parse(path)
        except OSError:
            return
        milliseconds = media_info.tracks[0].duration

        (hours, milliseconds) = divmod(milliseconds, 3600 * 1000)
        (minutes, milliseconds) = divmod(milliseconds, 60 * 1000)
        (seconds, milliseconds) = divmod(milliseconds, 1000)

        formatted = f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"
        return formatted
