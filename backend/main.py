import os
import sys
import io
from contextlib import asynccontextmanager

# Configure Windows terminal encoding to UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.services.auth_service import AuthService
from backend.routers import (
    chat_router,
    quiz_router,
    progress_router,
    documents_router,
    auth_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Auto-create PostgreSQL tables and ensure default demo account
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            AuthService.ensure_demo_student(db)
        finally:
            db.close()
        print("[SUCCESS] Database tables and demo student verified in PostgreSQL")
    except Exception as e:
        print(f"[WARNING] Database initialization warning: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent AI Tutor API with Groq LLM, Student Authentication, and PostgreSQL persistence.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(quiz_router)
app.include_router(progress_router)
app.include_router(documents_router)

# Health endpoint
@app.get("/health", tags=["General"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "model": settings.GROQ_MODEL
    }

# Serve Frontend App at root
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", tags=["Frontend"])
    def serve_frontend():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend index.html not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
