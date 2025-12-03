from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routers import auth, cafe, order, public, worker, worker_request, upload, feedback, admin
from app.websockets import routes as ws_routes
from app.database import Base, engine
from app import models

app = FastAPI(title="Canteen Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

Base.metadata.create_all(engine)
app.include_router(auth.router)
app.include_router(cafe.router)
app.include_router(order.router)
app.include_router(public.router)
app.include_router(worker.router)
app.include_router(worker_request.router)
app.include_router(upload.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(ws_routes.router)
