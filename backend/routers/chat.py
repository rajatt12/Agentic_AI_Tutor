from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.schemas import ChatRequest, ChatResponse
from backend.services.agent_service import agent_service

router = APIRouter(prefix="/api/v1/chat", tags=["Chat & Learning"])

@router.post("", response_model=ChatResponse)
def handle_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process student input:
    - Classifies intent (Explanation, Quiz, Progress Check, Chat)
    - Retrieves grounded study notes via Hybrid Search
    - Returns structured explanation + auto-generated practice questions
    """
    try:
        result = agent_service.process_chat(
            db=db,
            student_id=request.student_id,
            query=request.query,
            api_key=request.groq_api_key,
            model=request.groq_model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
