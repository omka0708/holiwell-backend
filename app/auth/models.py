from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String

from app.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    path_to_avatar = Column(String)
