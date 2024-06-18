from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Trainer(Base):
    __tablename__ = "trainer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    description = Column(String)
    path_to_avatar = Column(String)
    path_to_background = Column(String)

    lessons = relationship("Lesson", back_populates="trainer", lazy='selectin')
