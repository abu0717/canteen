import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    order_id = Column(Integer, ForeignKey("order.id", ondelete="CASCADE"))
    comment = Column(Text, nullable=False)
    rating = Column(Float, default=1)
    cafe_id = Column(String(36), ForeignKey("cafe.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.now)
    student = relationship("User", back_populates="feedbacks")
    cafe = relationship("Cafe", back_populates="feedbacks")
    order = relationship("Order", back_populates="feedback")
