from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.routers.auth import get_current_user
from pydantic import BaseModel
from typing import List
from uuid import uuid4


router = APIRouter(
    prefix="/worker-requests",
    tags=["Worker Requests"],
)


class WorkerRequestCreate(BaseModel):
    cafe_id: str


class WorkerRequestUpdate(BaseModel):
    status: str  # 'approved' or 'rejected'


class WorkerRequestResponse(BaseModel):
    id: str
    user_id: str
    cafe_id: str
    status: str
    user_name: str
    user_email: str
    cafe_name: str
    created_at: str


@router.post("/", response_model=WorkerRequestResponse)
def create_worker_request(
    request: WorkerRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Worker creates a request to join a cafe"""
    if current_user["role"] != "cafe_worker":
        raise HTTPException(
            status_code=403,
            detail="Only cafe workers can create requests"
        )

    # Check if cafe exists
    cafe = db.execute(
        text("SELECT id, name FROM cafe WHERE id = :cafe_id"),
        {"cafe_id": request.cafe_id}
    ).fetchone()

    if not cafe:
        raise HTTPException(status_code=404, detail="Cafe not found")

    # Check if already assigned
    existing_assignment = db.execute(
        text("SELECT id FROM cafe_worker WHERE user_id = :user_id AND cafe_id = :cafe_id"),
        {"user_id": current_user["id"], "cafe_id": request.cafe_id}
    ).fetchone()

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="You are already assigned to this cafe"
        )

    # Check if request already exists
    existing_request = db.execute(
        text("SELECT id, status FROM worker_request WHERE user_id = :user_id AND cafe_id = :cafe_id"),
        {"user_id": current_user["id"], "cafe_id": request.cafe_id}
    ).fetchone()

    if existing_request:
        if existing_request[1] == "pending":
            raise HTTPException(
                status_code=400,
                detail="You already have a pending request for this cafe"
            )
        elif existing_request[1] == "approved":
            raise HTTPException(
                status_code=400,
                detail="Your request was already approved"
            )

    request_id = str(uuid4())

    db.execute(
        text("""
            INSERT INTO worker_request (id, user_id, cafe_id, status, created_at, updated_at)
            VALUES (:id, :user_id, :cafe_id, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """),
        {"id": request_id, "user_id": current_user["id"], "cafe_id": request.cafe_id}
    )

    db.commit()

    user = db.execute(
        text("SELECT name, email FROM \"user\" WHERE id = :user_id"),
        {"user_id": current_user["id"]}
    ).fetchone()

    return {
        "id": request_id,
        "user_id": current_user["id"],
        "cafe_id": cafe[0],
        "status": "pending",
        "user_name": user[0],
        "user_email": user[1],
        "cafe_name": cafe[1],
        "created_at": str(db.execute(text("SELECT CURRENT_TIMESTAMP")).fetchone()[0])
    }


@router.get("/cafe/{cafe_id}", response_model=List[WorkerRequestResponse])
def get_cafe_requests(
    cafe_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all worker requests for a cafe (owner only)"""
    # Verify cafe ownership
    cafe_check = db.execute(
        text("SELECT id FROM cafe WHERE id = :cafe_id AND owner_id = :owner_id"),
        {"cafe_id": cafe_id, "owner_id": current_user["id"]}
    ).fetchone()

    if not cafe_check:
        raise HTTPException(
            status_code=404,
            detail="Cafe not found or you don't have access"
        )

    requests = db.execute(
        text("""
            SELECT wr.id, wr.user_id, wr.cafe_id, wr.status, wr.created_at,
                   u.name as user_name, u.email as user_email, c.name as cafe_name
            FROM worker_request wr
            JOIN "user" u ON wr.user_id = u.id
            JOIN cafe c ON wr.cafe_id = c.id
            WHERE wr.cafe_id = :cafe_id AND wr.status = 'pending'
            ORDER BY wr.created_at DESC
        """),
        {"cafe_id": cafe_id}
    ).mappings().fetchall()

    return requests


@router.put("/{request_id}", response_model=WorkerRequestResponse)
def update_request_status(
    request_id: str,
    update: WorkerRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject a worker request (owner only)"""
    if update.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be 'approved' or 'rejected'"
        )

    # Get request and verify ownership
    request_data = db.execute(
        text("""
            SELECT wr.id, wr.user_id, wr.cafe_id, wr.status,
                   c.owner_id, u.name as user_name, u.email as user_email, c.name as cafe_name
            FROM worker_request wr
            JOIN cafe c ON wr.cafe_id = c.id
            JOIN "user" u ON wr.user_id = u.id
            WHERE wr.id = :request_id
        """),
        {"request_id": request_id}
    ).fetchone()

    if not request_data:
        raise HTTPException(status_code=404, detail="Request not found")

    if request_data[4] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this request"
        )

    if request_data[3] != "pending":
        raise HTTPException(
            status_code=400,
            detail="Request has already been processed"
        )

    # Update request status
    db.execute(
        text("""
            UPDATE worker_request
            SET status = :status, updated_at = CURRENT_TIMESTAMP
            WHERE id = :request_id
        """),
        {"request_id": request_id, "status": update.status}
    )

    # If approved, create cafe_worker assignment
    if update.status == "approved":
        worker_id = str(uuid4())
        db.execute(
            text("""
                INSERT INTO cafe_worker (id, user_id, cafe_id, created_at, updated_at)
                VALUES (:id, :user_id, :cafe_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """),
            {"id": worker_id, "user_id": request_data[1], "cafe_id": request_data[2]}
        )

    db.commit()

    return {
        "id": request_id,
        "user_id": request_data[1],
        "cafe_id": request_data[2],
        "status": update.status,
        "user_name": request_data[5],
        "user_email": request_data[6],
        "cafe_name": request_data[7],
        "created_at": str(request_data[3])
    }
