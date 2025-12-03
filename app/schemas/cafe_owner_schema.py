import datetime

from pydantic import BaseModel


class CafeOwnerResponse(BaseModel):
    id: str
    name: str
    email: str
    total_orders: int
    total_customers: int
    total_revenue: int
    cafe_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CafeOwnerCreate(BaseModel):
    user_id: int
