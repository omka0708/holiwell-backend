from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    path_to_avatar = Column(String)

    planned_lessons = relationship("PlannedLesson", back_populates="user")


class PlannedLesson(Base):
    __tablename__ = "planned_lesson"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="planned_lessons", lazy='selectin')

    lesson_id = Column(Integer, ForeignKey("lesson.id"))
    lesson = relationship("Lesson", back_populates="planned_lessons", lazy='selectin')
