from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.schemas import ProgressResponse
from backend.services.student_service import StudentService

router = APIRouter(prefix="/api/v1/progress", tags=["Student Progress"])

@router.get("/{student_id}", response_model=ProgressResponse)
def get_student_progress(student_id: str, db: Session = Depends(get_db)):
    """
    Retrieve comprehensive student mastery metrics, topic breakdown,
    quiz count, and personalized recommendations from PostgreSQL.
    """
    try:
        report = StudentService.get_progress_report(db, student_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch progress: {str(e)}")
