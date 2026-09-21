"""
Database Connection & Inspection Utility
Run: python test_db.py
"""
import os
from sqlalchemy import text
from backend.database import engine, Base, SessionLocal
from backend.models.models import Student, TopicPerformance, QuizAttempt, QuizQuestion
from backend.services.student_service import StudentService

def test_database():
    print("=" * 60)
    print("🔍 Testing Database Connection & PostgreSQL Tables")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"✅ Connection successful! Query result: {result}")
            print(f"📡 Database Engine URL: {engine.url}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Create tables
    print("\n📦 Verifying / Creating Tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables verified:")
    for table_name in Base.metadata.tables.keys():
        print(f"   • {table_name}")

    # Test CRUD operations
    db = SessionLocal()
    try:
        print("\n🧪 Testing Student CRUD in PostgreSQL...")
        student = StudentService.get_or_create_student(db, "student_demo", "Demo Learner")
        print(f"✅ Created/Loaded Student: ID={student.student_id}, Name={student.name}")

        # Update test performance
        perf = StudentService.update_topic_performance(db, "student_demo", "Algebra Basics", 85.0)
        print(f"✅ Recorded Topic Performance: Topic={perf.topic}, Accuracy={perf.accuracy}%, Strength={perf.strength}")

        # Fetch progress report
        report = StudentService.get_progress_report(db, "student_demo")
        print(f"✅ Progress Report Compiled: Total Quizzes={report['total_quizzes']}, Topics={report['topics_practiced']}")
    except Exception as e:
        print(f"❌ Error during CRUD test: {e}")
    finally:
        db.close()

    print("\n🎉 Database test completed successfully!")

if __name__ == "__main__":
    test_database()
