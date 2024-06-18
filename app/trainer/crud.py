from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.trainer import models, schemas
from app.utils import upload_file, delete_file


async def create_trainer(trainer: schemas.TrainerCreate, avatar: UploadFile, background: UploadFile, db: AsyncSession):
    trainer_dict = trainer.model_dump()
    trainer_dict['path_to_avatar'] = upload_file('trainers/avatar', avatar, avatar.filename)
    trainer_dict['path_to_background'] = upload_file('trainers/background', background, background.filename)

    db_trainer = models.Trainer(**trainer_dict)
    db.add(db_trainer)

    await db.commit()
    return db_trainer


async def get_trainer(trainer_id: int, db: AsyncSession):
    db_trainer = await db.get(models.Trainer, trainer_id)
    if not db_trainer:
        return
    return db_trainer


async def get_trainers(db: AsyncSession):
    db_trainers = await db.execute(select(models.Trainer).limit(1000))
    obj_trainers = db_trainers.scalars().all()
    return obj_trainers


async def update_trainer(trainer_id: int, trainer: schemas.TrainerUpdate,
                         avatar: UploadFile, background: UploadFile, db: AsyncSession):
    db_trainer = await db.get(models.Trainer, trainer_id)
    if not db_trainer:
        return

    trainer_dict = trainer.model_dump(exclude_none=True)

    if avatar:
        delete_file(db_trainer.path_to_avatar)
        trainer_dict['path_to_avatar'] = upload_file('trainers/avatar', avatar, avatar.filename)
    if background:
        delete_file(db_trainer.path_to_background)
        trainer_dict['path_to_background'] = upload_file('trainers/background', background, background.filename)

    for key, value in trainer_dict.items():
        setattr(db_trainer, key, value)

    await db.commit()
    return db_trainer


async def delete_trainer(trainer_id: int, db: AsyncSession):
    db_trainer = await db.get(models.Trainer, trainer_id)
    if not db_trainer:
        return

    try:
        delete_file(db_trainer.path_to_avatar)
        delete_file(db_trainer.path_to_background)
    except FileNotFoundError:
        pass

    await db.delete(db_trainer)
    await db.commit()
    return True
