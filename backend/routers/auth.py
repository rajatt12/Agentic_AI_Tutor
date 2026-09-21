from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import Student
from backend.schemas.schemas import (
    RegisterRequest,
    LoginRequest,
    StudentProfile,
    AuthResponse
)
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Student Authentication"])

@router.post("/register", response_model=AuthResponse)
def register_student(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new student profile in PostgreSQL"""
    try:
        student = AuthService.register_student(
            db=db,
            username=payload.username,
            full_name=payload.full_name,
            password=payload.password,
            target_exam=payload.target_exam or "Competitive Exams"
        )
        return AuthResponse(
            status="success",
            message=f"Welcome {student.full_name}!",
            student=StudentProfile(
                student_id=student.student_id,
                username=student.username,
                full_name=student.full_name,
                target_exam=student.target_exam or "Competitive Exams",
                created_at=student.created_at.isoformat() if student.created_at else None
            ),
            token=f"token_{student.student_id}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.post("/login", response_model=AuthResponse)
def login_student(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate student username and password"""
    try:
        student = AuthService.authenticate_student(
            db=db,
            username=payload.username,
            password=payload.password
        )
        return AuthResponse(
            status="success",
            message=f"Logged in as {student.full_name}",
            student=StudentProfile(
                student_id=student.student_id,
                username=student.username or student.student_id,
                full_name=student.full_name or student.student_id,
                target_exam=student.target_exam or "Competitive Exams",
                created_at=student.created_at.isoformat() if student.created_at else None
            ),
            token=f"token_{student.student_id}"
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@router.get("/me/{student_id}", response_model=StudentProfile)
def get_current_student(student_id: str, db: Session = Depends(get_db)):
    """Get student profile details"""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return StudentProfile(
        student_id=student.student_id,
        username=student.username or student.student_id,
        full_name=student.full_name or student.student_id,
        target_exam=student.target_exam or "Competitive Exams",
        created_at=student.created_at.isoformat() if student.created_at else None
    )


@router.get("/students", response_model=List[StudentProfile])
def list_students(db: Session = Depends(get_db)):
    """List registered student accounts for quick profile switching"""
    # Ensure demo student exists
    AuthService.ensure_demo_student(db)
    students = db.query(Student).all()
    return [
        StudentProfile(
            student_id=s.student_id,
            username=s.username or s.student_id,
            full_name=s.full_name or s.student_id,
            target_exam=s.target_exam or "Competitive Exams",
            created_at=s.created_at.isoformat() if s.created_at else None
        )
        for s in students
    ]
