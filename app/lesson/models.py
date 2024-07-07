from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Lesson(Base):
    __tablename__ = "lesson"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    path_to_cover = Column(String)
    path_to_video = Column(String)
    path_to_audio = Column(String)

    trainer_id = Column(Integer, ForeignKey("trainer.id"))
    trainer = relationship("Trainer", back_populates="lessons", lazy='selectin')

    course_id = Column(Integer, ForeignKey("course.id"))
    course = relationship("Course", back_populates="lessons", lazy='selectin')

    planned_lessons = relationship("PlannedLesson", back_populates="lesson", cascade="all, delete")
    views = relationship("View", back_populates="lesson", cascade="all, delete")
    favorites = relationship("Favorite", back_populates="lesson", cascade="all, delete")


class LinkBeforeLesson(Base):
    __tablename__ = "link_before_lesson"
    id = Column(Integer, primary_key=True, autoincrement=True)

    lesson_id = Column(Integer, ForeignKey("lesson.id", ondelete="cascade"))
    linked_lesson_id = Column(Integer, ForeignKey("lesson.id", ondelete="cascade"))


class LinkAfterLesson(Base):
    __tablename__ = "link_after_lesson"
    id = Column(Integer, primary_key=True, autoincrement=True)

    lesson_id = Column(Integer, ForeignKey("lesson.id", ondelete="cascade"))
    linked_lesson_id = Column(Integer, ForeignKey("lesson.id", ondelete="cascade"))
