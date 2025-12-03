import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CafeWorker(Base):
    __tablename__ = 'cafe_worker'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    cafe_id = Column(String(36), ForeignKey('cafe.id', ondelete='CASCADE'), nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

