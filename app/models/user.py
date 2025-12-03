import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, Enum):
    student = 'student'
    cafe_owner = 'cafe_owner'
    cafe_worker = 'cafe_worker'
    admin = 'admin'


class User(Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default=UserRole.student.value)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    feedbacks = relationship("Feedback", back_populates="student", cascade="all, delete-orphan")
