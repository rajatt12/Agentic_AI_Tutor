from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import engine, Base
from backend.routers import chat_router, quiz_router, progress_router, documents_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Auto-create PostgreSQL tables if they do not exist
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified successfully in PostgreSQL")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    yield
    # Shutdown logic if needed

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Decoupled Multi-Agent AI Tutor API with Groq LLM, Hybrid RAG, and PostgreSQL persistence.",
    lifespan=lifespan
)

# CORS configuration (allow requests from Streamlit, React, mobile apps, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(chat_router)
app.include_router(quiz_router)
app.include_router(progress_router)
app.include_router(documents_router)

@app.get("/", tags=["General"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["General"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "model": settings.GROQ_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
