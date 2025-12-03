import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import User
from app.models.cafe import Cafe


class AdvertisementBanner(Base):
    __tablename__ = "advertisement_banner"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image = Column(String, nullable=False)
    link = Column(String, nullable=True)
    cafe_id = Column(String(36), ForeignKey("cafe.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cafe = relationship("Cafe", back_populates="advertisement_banners")
