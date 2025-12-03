from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class FeedbackCreateSchema(BaseModel):
    order_id: int
    rating: float
    comment: str


class FeedbackResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    order_id: int
    comment: str
    rating: float
    cafe_id: str
    created_at: Optional[datetime] = None