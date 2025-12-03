import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey,
    Integer, Float, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class Cafe(Base):
    __tablename__ = "cafe"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    image = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("cafe_owner_profile.id", ondelete="CASCADE"))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    rating = Column(Float, default=4.0)
    categories = relationship("Category", back_populates="cafe", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="cafe", cascade="all, delete-orphan")
    inventory_items = relationship("Inventory", back_populates="cafe", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="cafe", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "category"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cafe_id = Column(String(36), ForeignKey("cafe.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    cafe = relationship("Cafe", back_populates="categories")
    menu_items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")


class PublicCategory(Base):
    __tablename__ = "public_category"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    image = Column(String, nullable=True)

class MenuItem(Base):
    __tablename__ = "menu_item"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cafe_id = Column(String(36), ForeignKey("cafe.id", ondelete="CASCADE"))
    category_id = Column(String(36), ForeignKey("category.id", ondelete="SET NULL"))

    image = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    cafe = relationship("Cafe", back_populates="menu_items")
    category = relationship("Category", back_populates="menu_items")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cafe_id = Column(String(36), ForeignKey("cafe.id", ondelete="CASCADE"))

    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    kg = Column(Float, nullable=False)
    description = Column(String, nullable=True)

    cafe_owner_id = Column(Integer, ForeignKey("cafe_owner_profile.id", ondelete="CASCADE"))

    cafe = relationship("Cafe", back_populates="inventory_items")
