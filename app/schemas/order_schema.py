from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.models.order import StatusTypes


class OrderItemCreateSchema(BaseModel):
    menu_item_id: str
    quantity: int
    scheduled: bool = False
    scheduled_time: Optional[datetime] = None


class OrderItemResponseSchema(BaseModel):
    id: int
    order_id: int
    menu_item_id: str
    menu_item_name: str
    quantity: int
    price: float
    scheduled: bool
    scheduled_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderCreateSchema(BaseModel):
    cafe_id: str
    note: Optional[str] = None
    items: List[OrderItemCreateSchema]


class OrderUpdateSchema(BaseModel):
    status: Optional[StatusTypes] = None
    note: Optional[str] = None


class OrderResponseSchema(BaseModel):
    id: int
    account_id: str
    cafe_id: str
    note: Optional[str]
    status: str
    total_price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponseSchema(BaseModel):
    id: int
    account_id: str
    account_name: str
    cafe_id: str
    cafe_name: str
    note: Optional[str]
    status: str
    total_price: float
    items: List[OrderItemResponseSchema]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

