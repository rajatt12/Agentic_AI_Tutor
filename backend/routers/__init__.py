from backend.routers.chat import router as chat_router
from backend.routers.quiz import router as quiz_router
from backend.routers.progress import router as progress_router
from backend.routers.documents import router as documents_router

__all__ = ["chat_router", "quiz_router", "progress_router", "documents_router"]
