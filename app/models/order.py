import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class StatusTypes(str, Enum):
    pending = 'pending'
    preparing = 'preparing'
    ready = 'ready'
    completed = 'completed'
    cancelled = 'cancelled'


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    account_id = Column(String, ForeignKey('user.id'), nullable=False)
    cafe_id = Column(String(36), ForeignKey('cafe.id'), nullable=False)
    note = Column(String, nullable=True)
    status = Column(String, default=StatusTypes.pending.value)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = Column(String(36), ForeignKey('menu_item.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    scheduled = Column(Boolean, default=False)
    scheduled_time = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    order = relationship("Order", back_populates="items")
