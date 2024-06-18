from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import fastapi_users
from app.auth.models import User
from app.database import get_async_session
from app.trainer import schemas, crud

router = APIRouter()


@router.post("/create", response_model=schemas.TrainerCreate)
async def create_trainer(first_name: Annotated[str, Form()],
                         last_name: Annotated[str, Form()],
                         description: Annotated[str, Form()],
                         avatar: UploadFile = File(...), background: UploadFile = File(...),
                         user: User = Depends(fastapi_users.current_user(superuser=True)),
                         session: AsyncSession = Depends(get_async_session)):
    trainer = schemas.TrainerCreate(first_name=first_name,
                                    last_name=last_name,
                                    description=description)
    await crud.create_trainer(trainer, avatar, background, session)
    return Response(status_code=201)


@router.get("/all", response_model=list[schemas.TrainerRead])
async def read_trainers(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_trainers(session)


@router.get("/{trainer_id}", response_model=schemas.TrainerRead)
async def read_trainer(trainer_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await crud.get_trainer(trainer_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Trainer {trainer_id} doesn't exist."
        })
    return result


@router.patch("/{trainer_id}", response_model=schemas.TrainerUpdate)
async def update_trainer(trainer_id: int,
                         first_name: Annotated[str | None, Form()] = None,
                         last_name: Annotated[str | None, Form()] = None,
                         description: Annotated[str | None, Form()] = None,
                         avatar: UploadFile = None, background: UploadFile = None,
                         user: User = Depends(fastapi_users.current_user(superuser=True)),
                         session: AsyncSession = Depends(get_async_session)):
    trainer = schemas.TrainerUpdate(first_name=first_name,
                                    last_name=last_name,
                                    description=description)

    result = await crud.update_trainer(trainer_id, trainer, avatar, background, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Trainer {trainer_id} doesn't exist."
        })
    return Response(status_code=204)


@router.delete("/{trainer_id}")
async def delete_trainer(trainer_id: int,
                         user: User = Depends(fastapi_users.current_user(superuser=True)),
                         session: AsyncSession = Depends(get_async_session)):
    result = await crud.delete_trainer(trainer_id, session)
    if not result:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "msg": f"Trainer {trainer_id} doesn't exist."
        })
    return Response(status_code=204)
