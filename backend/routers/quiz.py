from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.schemas import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuizQuestionResult
)
from backend.services.agent_service import agent_service
from backend.services.student_service import StudentService

router = APIRouter(prefix="/api/v1/quiz", tags=["Adaptive Quizzes"])

@router.post("/generate", response_model=QuizGenerateResponse)
def generate_quiz(request: QuizGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate an adaptive multiple-choice quiz on a topic.
    Difficulty is automatically tailored based on the student's historical performance in PostgreSQL.
    """
    try:
        quiz_data = agent_service.generate_adaptive_quiz(
            db=db,
            student_id=request.student_id,
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            api_key=request.groq_api_key,
            model=request.groq_model
        )
        return quiz_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.post("/submit", response_model=QuizSubmitResponse)
def submit_quiz(submission: QuizSubmitRequest, db: Session = Depends(get_db)):
    """
    Submit completed quiz answers:
    - Auto-grades each answer
    - Stores the quiz attempt and each question in PostgreSQL
    - Recalculates the student's rolling topic accuracy & strength
    """
    try:
        record = StudentService.record_quiz_attempt(
            db=db,
            student_id=submission.student_id,
            topic=submission.topic,
            difficulty=submission.difficulty,
            questions_data=submission.questions
        )

        attempt = record["attempt"]
        topic_perf = record["topic_perf"]
        
        results_list = [
            QuizQuestionResult(
                id=i + 1,
                question=eq["question"],
                user_answer=eq["user_answer"],
                correct_answer=eq["correct_answer"],
                is_correct=eq["is_correct"],
                explanation=eq["explanation"]
            )
            for i, eq in enumerate(record["evaluated_questions"])
        ]

        return QuizSubmitResponse(
            student_id=submission.student_id,
            topic=submission.topic,
            score=attempt.score,
            total_questions=attempt.total_questions,
            accuracy=attempt.accuracy,
            updated_topic_accuracy=round(topic_perf.accuracy, 1),
            updated_topic_strength=topic_perf.strength,
            results=results_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz submission failed: {str(e)}")
