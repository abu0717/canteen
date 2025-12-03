from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# PostgreSQL engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using
    pool_size=10,            # Connection pool size
    max_overflow=20,         # Max overflow connections
    echo=False               # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
