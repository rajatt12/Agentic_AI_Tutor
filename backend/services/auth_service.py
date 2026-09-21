import hashlib
import secrets
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.models import Student

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with a secure random salt using PBKDF2-HMAC-SHA256"""
        salt = secrets.token_hex(16)
        iterations = 100_000
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        return f"{salt}${iterations}${key.hex()}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against the stored salt$iterations$key string"""
        try:
            if not hashed_password or '$' not in hashed_password:
                # Plaintext fallback for legacy dev records
                return plain_password == hashed_password

            salt, iterations_str, stored_key = hashed_password.split('$')
            iterations = int(iterations_str)
            key = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations
            )
            return secrets.compare_digest(key.hex(), stored_key)
        except Exception:
            return False

    @staticmethod
    def register_student(
        db: Session,
        username: str,
        full_name: str,
        password: str,
        target_exam: str = "Competitive Exams"
    ) -> Student:
        """Register a new student account"""
        clean_username = username.strip().lower()
        existing = db.query(Student).filter(
            (Student.username == clean_username) | (Student.student_id == clean_username)
        ).first()

        if existing:
            raise ValueError(f"Username '{username}' is already taken.")

        student = Student(
            student_id=clean_username,
            username=clean_username,
            full_name=full_name.strip(),
            hashed_password=AuthService.hash_password(password),
            target_exam=target_exam.strip() or "Competitive Exams",
            created_at=datetime.utcnow()
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def authenticate_student(db: Session, username: str, password: str) -> Student:
        """Authenticate student credentials"""
        clean_username = username.strip().lower()
        student = db.query(Student).filter(
            (Student.username == clean_username) | (Student.student_id == clean_username)
        ).first()

        if not student:
            raise ValueError("Student username not found.")

        if student.hashed_password and not AuthService.verify_password(password, student.hashed_password):
            raise ValueError("Invalid password.")

        return student

    @staticmethod
    def ensure_demo_student(db: Session) -> Student:
        """Ensure a default demo student exists for instant testing"""
        demo = db.query(Student).filter(Student.student_id == "demo_student").first()
        if not demo:
            demo = Student(
                student_id="demo_student",
                username="demo",
                full_name="Demo Learner",
                hashed_password=AuthService.hash_password("demo123"),
                target_exam="JEE & SAT",
                created_at=datetime.utcnow()
            )
            db.add(demo)
            db.commit()
            db.refresh(demo)
        return demo
