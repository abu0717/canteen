from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


# -----------------------------
# CAFE
# -----------------------------

class CafeCreateSchema(BaseModel):
    name: str
    location: str
    image: Optional[str] = None


class CafeUpdateSchema(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    image: Optional[str] = None


class CafeResponseSchema(BaseModel):
    id: str
    name: str
    location: str
    image: Optional[str] = None
    owner_id: str
    rating: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# CATEGORY
# -----------------------------

class CafeCategoryCreateSchema(BaseModel):
    cafe_id: str
    name: str


class CafeCategoryResponseSchema(BaseModel):
    id: str
    cafe_id: str
    name: str

    class Config:
        from_attributes = True


# -----------------------------
# MENU ITEM
# -----------------------------

class CafeMenuItemCreateSchema(BaseModel):
    cafe_id: str
    category_id: Optional[str] = None
    image: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: float
    available: bool = True


class CafeMenuItemUpdateSchema(BaseModel):
    category_id: Optional[str] = None
    image: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None


class CafeMenuItemResponseSchema(BaseModel):
    id: str
    cafe_id: str
    category_id: Optional[str]
    image: Optional[str]
    name: str
    description: Optional[str]
    price: float
    available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# INVENTORY
# -----------------------------

class CafeInventoryCreateSchema(BaseModel):
    cafe_id: str
    name: str
    quantity: float
    kg: float
    description: Optional[str] = None
    cafe_owner_id: str


class CafeInventoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    kg: Optional[float] = None
    description: Optional[str] = None
    cafe_owner_id: Optional[str] = None


class CafeInventoryResponseSchema(BaseModel):
    id: str
    cafe_id: str
    name: str
    quantity: float
    kg: float
    description: Optional[str]
    cafe_owner_id: str

    class Config:
        from_attributes = True


# -----------------------------
# NESTED RESPONSES (Optional but useful)
# -----------------------------

class CafeFullResponseSchema(BaseModel):
    id: str
    name: str
    location: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    categories: List[CafeCategoryResponseSchema]
    menu_items: List[CafeMenuItemResponseSchema]
    inventory_items: List[CafeInventoryResponseSchema]

    class Config:
        from_attributes = True


class PublicCategoryResponseSchema(BaseModel):
    id: str
    name: str
    image: Optional[str]

    class Config:
        from_attributes = True

class PublicCategoryCreateSchema(BaseModel):
    name: str
    image: Optional[str] = None

class PublicCategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None

