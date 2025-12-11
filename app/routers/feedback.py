from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from uuid import uuid4
from app.database import get_db
from app.schemas.feedback_schema import FeedbackCreateSchema, FeedbackResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse)
def create_feedback(
    feedback: FeedbackCreateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    feedback_id = str(uuid4())
    student_id = current_user["id"]
    
    order_check = db.execute(
        text("SELECT cafe_id, account_id FROM \"order\" WHERE id = :order_id and status = 'completed'"),
        {"order_id": feedback.order_id}
    ).fetchone()
    
    if not order_check:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order_check[1] != student_id:
        raise HTTPException(status_code=403, detail="You can only provide feedback for your own orders")
    
    cafe_id = order_check[0]
    
    existing_feedback = db.execute(
        text("SELECT id FROM feedback WHERE order_id = :order_id"),
        {"order_id": feedback.order_id}
    ).fetchone()
    
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback already exists for this order")
    
    # Insert feedback
    now = db.execute(text("SELECT CURRENT_TIMESTAMP")).fetchone()[0]
    
    db.execute(text("""
        INSERT INTO feedback (id, student_id, order_id, comment, rating, cafe_id, created_at)
        VALUES (:id, :student_id, :order_id, :comment, :rating, :cafe_id, :created_at)
    """), {
        "id": feedback_id,
        "student_id": student_id,
        "order_id": feedback.order_id,
        "comment": feedback.comment,
        "rating": feedback.rating,
        "cafe_id": cafe_id,
        "created_at": now,
    })
    
    db.commit()
    
    # Get student name
    student_name = db.execute(
        text("SELECT name FROM users WHERE id = :id"),
        {"id": student_id}
    ).fetchone()[0]
    
    return {
        "id": feedback_id,
        "student_id": str(student_id),
        "student_name": student_name,
        "order_id": feedback.order_id,
        "comment": feedback.comment,
        "rating": feedback.rating,
        "cafe_id": cafe_id,
        "created_at": now,
    }


@router.get("/cafe/{cafe_id}", response_model=List[FeedbackResponse])
def get_cafe_feedbacks(
    cafe_id: str,
    db: Session = Depends(get_db)
):
    """Get all feedbacks for a specific cafe."""
    query = text("""
        SELECT f.id, f.student_id, f.order_id, f.comment, f.rating, f.cafe_id, f.created_at,
               u.name as student_name
        FROM feedback f
        JOIN users u ON f.student_id = u.id
        WHERE f.cafe_id = :cafe_id
        ORDER BY f.created_at DESC
    """)
    
    result = db.execute(query, {"cafe_id": cafe_id})
    rows = result.mappings().fetchall()
    
    return [dict(row) for row in rows]


@router.get("/owner/feedbacks", response_model=List[FeedbackResponse])
def get_owner_feedbacks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all feedbacks for cafes owned by the current user."""
    query = text("""
        SELECT f.id, f.student_id, f.order_id, f.comment, f.rating, f.cafe_id, f.created_at,
               u.name as student_name
        FROM feedback f
        JOIN users u ON f.student_id = u.id
        JOIN cafe c ON f.cafe_id = c.id
        JOIN cafe_owner_profile cop ON c.owner_id = cop.id
        WHERE cop.user_id = :user_id
        ORDER BY f.created_at DESC
    """)
    
    result = db.execute(query, {"user_id": current_user["id"]})
    rows = result.mappings().fetchall()
    
    return [dict(row) for row in rows]


@router.get("/my-feedbacks", response_model=List[FeedbackResponse])
def get_my_feedbacks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all feedbacks submitted by the current user."""
    query = text("""
        SELECT f.id, f.student_id, f.order_id, f.comment, f.rating, f.cafe_id, f.created_at,
               u.name as student_name
        FROM feedback f
        JOIN users u ON f.student_id = u.id
        WHERE f.student_id = :student_id
        ORDER BY f.created_at DESC
    """)
    
    result = db.execute(query, {"student_id": current_user["id"]})
    rows = result.mappings().fetchall()
    
    return [dict(row) for row in rows]


@router.get("/order/{order_id}", response_model=FeedbackResponse)
def get_order_feedback(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get feedback for a specific order."""
    query = text("""
        SELECT f.id, f.student_id, f.order_id, f.comment, f.rating, f.cafe_id, f.created_at,
               u.name as student_name
        FROM feedback f
        JOIN users u ON f.student_id = u.id
        WHERE f.order_id = :order_id
    """)
    
    result = db.execute(query, {"order_id": order_id})
    row = result.mappings().fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="No feedback found for this order")
    
    return dict(row)


@router.delete("/{feedback_id}")
def delete_feedback(
    feedback_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a feedback. Only the student who created it can delete it."""
    # Check if feedback exists and belongs to current user
    feedback_check = db.execute(
        text("SELECT student_id FROM feedback WHERE id = :id"),
        {"id": feedback_id}
    ).fetchone()
    
    if not feedback_check:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    if feedback_check[0] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own feedback"
        )
    
    db.execute(
        text("DELETE FROM feedback WHERE id = :id"),
        {"id": feedback_id}
    )
    db.commit()
    
    return {"message": "Feedback deleted successfully"}
