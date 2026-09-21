from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=True)
    email = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topics = relationship("TopicPerformance", back_populates="student", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")


class TopicPerformance(Base):
    __tablename__ = "topic_performances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), index=True)
    topic = Column(String(128), index=True, nullable=False)
    accuracy = Column(Float, default=0.0)
    attempts = Column(Integer, default=0)
    strength = Column(String(32), default="unknown")  # strong, medium, weak, unknown
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="topics")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.student_id", ondelete="CASCADE"), index=True)
    topic = Column(String(128), index=True, nullable=False)
    difficulty = Column(String(32), default="medium")  # easy, medium, hard
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="quiz_attempts")
    questions = relationship("QuizQuestion", back_populates="quiz_attempt", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), index=True)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of string options
    user_answer = Column(String(16), nullable=True)
    correct_answer = Column(String(16), nullable=False)
    is_correct = Column(Boolean, default=False)
    explanation = Column(Text, nullable=True)

    # Relationships
    quiz_attempt = relationship("QuizAttempt", back_populates="questions")


class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(64), default="notes")  # notes, pdf, book
    created_at = Column(DateTime, default=datetime.utcnow)
