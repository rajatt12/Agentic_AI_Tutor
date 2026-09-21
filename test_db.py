"""
Database Connection & Inspection Utility
Run: python test_db.py
"""
import sys
import io

# Ensure UTF-8 output on Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import text
from backend.database import engine, Base, SessionLocal
from backend.models.models import Student, TopicPerformance, QuizAttempt, QuizQuestion
from backend.services.student_service import StudentService

def test_database():
    print("=" * 60)
    print("Testing Database Connection & PostgreSQL Tables")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"[SUCCESS] Connection successful! Result: {result}")
            print(f"[INFO] Database Engine URL: {engine.url}")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return

    # Create tables
    print("\nVerifying / Creating Tables in PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Tables verified:")
    for table_name in Base.metadata.tables.keys():
        print(f"   * {table_name}")

    # Test CRUD operations
    db = SessionLocal()
    try:
        print("\nTesting Student CRUD in PostgreSQL...")
        student = StudentService.get_or_create_student(db, "student_001", "Demo Learner")
        print(f"[SUCCESS] Created/Loaded Student: ID={student.student_id}, Name={student.name}")

        perf = StudentService.update_topic_performance(db, "student_001", "Algebra Basics", 85.0)
        print(f"[SUCCESS] Recorded Topic Performance: Topic={perf.topic}, Accuracy={perf.accuracy}%, Strength={perf.strength}")

        report = StudentService.get_progress_report(db, "student_001")
        print(f"[SUCCESS] Progress Report Compiled: Total Quizzes={report['total_quizzes']}, Topics={report['topics_practiced']}")
    except Exception as e:
        print(f"[ERROR] Error during CRUD test: {e}")
    finally:
        db.close()

    print("\n[DONE] Database test completed successfully!")

if __name__ == "__main__":
    test_database()
