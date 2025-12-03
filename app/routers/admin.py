from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, and_, select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.cafe import Cafe
from app.models.order import Order, OrderItem
from app.models.feedback import Feedback
from app.models.cafe import MenuItem

router = APIRouter(prefix="/admin", tags=["Admin"])


def verify_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    
    total_cafes = db.query(func.count(Cafe.id)).scalar()
    total_users = db.query(func.count(User.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_feedbacks = db.query(func.count(Feedback.id)).scalar()
    
    total_revenue = db.query(func.sum(Order.total_price)).filter(
        Order.status.in_(["completed", "ready", "preparing"])
    ).scalar() or 0
    
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    recent_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= thirty_days_ago
    ).scalar()
    previous_orders = db.query(func.count(Order.id)).filter(
        and_(Order.created_at >= sixty_days_ago, Order.created_at < thirty_days_ago)
    ).scalar()
    orders_growth = ((recent_orders - previous_orders) / previous_orders * 100) if previous_orders > 0 else 0
    
    recent_revenue = db.query(func.sum(Order.total_price)).filter(
        and_(
            Order.created_at >= thirty_days_ago,
            Order.status.in_(["completed", "ready", "preparing"])
        )
    ).scalar() or 0
    previous_revenue = db.query(func.sum(Order.total_price)).filter(
        and_(
            Order.created_at >= sixty_days_ago,
            Order.created_at < thirty_days_ago,
            Order.status.in_(["completed", "ready", "preparing"])
        )
    ).scalar() or 0
    revenue_growth = ((recent_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    
    recent_users = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago
    ).scalar()
    previous_users = db.query(func.count(User.id)).filter(
        and_(User.created_at >= sixty_days_ago, User.created_at < thirty_days_ago)
    ).scalar()
    users_growth = ((recent_users - previous_users) / previous_users * 100) if previous_users > 0 else 0
    
    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0
    
    return {
        "total_cafes": total_cafes,
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "total_feedbacks": total_feedbacks,
        "average_rating": float(avg_rating),
        "growth": {
            "orders": float(orders_growth),
            "revenue": float(revenue_growth),
            "users": float(users_growth)
        },
        "recent": {
            "orders_30d": recent_orders,
            "revenue_30d": float(recent_revenue),
            "users_30d": recent_users
        }
    }


@router.get("/cafes")
async def get_admin_cafes(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    
    cafes = db.query(Cafe).all()
    
    result = []
    for cafe in cafes:
        owner = db.query(User).filter(User.id == cafe.owner_id).first()
        
        total_orders = db.query(func.count(Order.id)).filter(
            Order.cafe_id == cafe.id
        ).scalar()
        
        total_revenue = db.query(func.sum(Order.total_price)).filter(
            and_(
                Order.cafe_id == cafe.id,
                Order.status.in_(["completed", "ready", "preparing"])
            )
        ).scalar() or 0
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders = db.query(func.count(Order.id)).filter(
            and_(
                Order.cafe_id == cafe.id,
                Order.created_at >= today_start
            )
        ).scalar()
        
        today_revenue = db.query(func.sum(Order.total_price)).filter(
            and_(
                Order.cafe_id == cafe.id,
                Order.created_at >= today_start,
                Order.status.in_(["completed", "ready", "preparing"])
            )
        ).scalar() or 0
        
        avg_rating = db.query(func.avg(Feedback.rating)).filter(
            Feedback.cafe_id == cafe.id
        ).scalar() or 0
        
        total_feedbacks = db.query(func.count(Feedback.id)).filter(
            Feedback.cafe_id == cafe.id
        ).scalar()
        
        result.append({
            "id": cafe.id,
            "name": cafe.name,
            "address": cafe.location,
            "image": cafe.image,
            "rating": cafe.rating,
            "owner": {
                "id": owner.id if owner else None,
                "name": owner.name if owner else "Unknown",
                "email": owner.email if owner else None
            },
            "statistics": {
                "total_orders": total_orders,
                "total_revenue": float(total_revenue),
                "today_orders": today_orders,
                "today_revenue": float(today_revenue),
                "average_rating": float(avg_rating),
                "total_feedbacks": total_feedbacks
            },
            "created_at": cafe.created_at.isoformat() if cafe.created_at else None
        })
    
    return result


@router.get("/users")
async def get_admin_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    
    users = db.query(User).all()
    
    result = []
    for user in users:
        stats = {}
        
        if user.role == "student":
            total_orders = db.query(func.count(Order.id)).filter(
                Order.account_id == user.id
            ).scalar()
            
            total_spent = db.query(func.sum(Order.total_price)).filter(
                and_(
                    Order.account_id == user.id,
                    Order.status.in_(["completed", "ready", "preparing"])
                )
            ).scalar() or 0
            
            total_feedbacks = db.query(func.count(Feedback.id)).filter(
                Feedback.student_id == user.id
            ).scalar()
            
            stats = {
                "total_orders": total_orders,
                "total_spent": float(total_spent),
                "total_feedbacks": total_feedbacks
            }
            
        elif user.role == "cafe_owner":
            cafes_count = db.query(func.count(Cafe.id)).filter(
                Cafe.owner_id == user.id
            ).scalar()
            
            stats = {
                "cafes_owned": cafes_count
            }
        
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "statistics": stats
        })
    
    return result


@router.get("/recent-activity")
async def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """Get recent system activity"""
    
    # Recent orders (last 10)
    recent_orders = db.query(Order, User, Cafe).join(
        User, Order.account_id == User.id
    ).join(
        Cafe, Order.cafe_id == Cafe.id
    ).order_by(Order.created_at.desc()).limit(10).all()
    
    orders_data = []
    for order, user, cafe in recent_orders:
        orders_data.append({
            "id": order.id,
            "user_name": user.name,
            "cafe_name": cafe.name,
            "total_price": float(order.total_price),
            "status": order.status,
            "created_at": order.created_at.isoformat()
        })
    
    recent_feedbacks = db.query(Feedback, User, Cafe).join(
        User, Feedback.student_id == User.id
    ).join(
        Cafe, Feedback.cafe_id == Cafe.id
    ).order_by(Feedback.created_at.desc()).limit(10).all()
    
    feedbacks_data = []
    for feedback, user, cafe in recent_feedbacks:
        feedbacks_data.append({
            "id": feedback.id,
            "user_name": user.name,
            "cafe_name": cafe.name,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "created_at": feedback.created_at.isoformat()
        })
    
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(10).all()
    
    users_data = []
    for user in recent_users:
        users_data.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return {
        "recent_orders": orders_data,
        "recent_feedbacks": feedbacks_data,
        "recent_users": users_data
    }
