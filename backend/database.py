import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

DATABASE_URL = settings.DATABASE_URL

# Connect to PostgreSQL or graceful fallback for dev testing
try:
    if DATABASE_URL.startswith("postgresql"):
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
except Exception as e:
    print(f"[WARNING] Could not create engine for {DATABASE_URL}: {e}")
    # Fallback to local SQLite
    DATABASE_URL = "sqlite:///./ai_tutor.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency: Yields a database session and ensures it closes afterwards"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
