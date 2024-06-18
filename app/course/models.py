from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Course(Base):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    path_to_cover = Column(String)

    course_type_id = Column(Integer, ForeignKey("course_type.id"))
    course_type = relationship("CourseType", back_populates="courses", lazy='selectin')

    lessons = relationship("Lesson", back_populates="course", lazy='selectin')


class CourseType(Base):
    __tablename__ = "course_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, unique=True)

    courses = relationship("Course", back_populates="course_type", lazy='selectin')
