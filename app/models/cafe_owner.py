import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from app.database import Base
from app.models.user import User


class CafeOwnerProfile(Base):
    __tablename__ = 'cafe_owner_profile'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'))
    total_orders = Column(String, default='0')
    total_customers = Column(String, default='0')
    total_revenue = Column(String, default='0')

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
