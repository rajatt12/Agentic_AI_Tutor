from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ----------------- Chat Schemas -----------------
class ChatRequest(BaseModel):
    student_id: str = Field(default="student_001", description="Unique student ID")
    query: str = Field(..., description="Student's message or question")
    groq_api_key: Optional[str] = Field(None, description="Optional override for Groq API key")
    groq_model: Optional[str] = Field(None, description="Optional override for Groq model")

class PracticeQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class ChatResponse(BaseModel):
    action: str
    response: Optional[str] = None
    explanation: Optional[str] = None
    practice_quiz: Optional[List[PracticeQuestion]] = None
    plan_executed: Optional[List[str]] = None
    topic: Optional[str] = None
    message: Optional[str] = None

# ----------------- Quiz Schemas -----------------
class QuizGenerateRequest(BaseModel):
    student_id: str = Field(default="student_001")
    topic: str
    num_questions: int = Field(default=3, ge=1, le=20)
    difficulty: Optional[str] = Field(None, description="easy, medium, hard, or leave None for auto-adaptive")
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None

class QuizQuestionItem(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuizGenerateResponse(BaseModel):
    topic: str
    difficulty: str
    questions: List[QuizQuestionItem]

class UserQuestionSubmission(BaseModel):
    id: int
    question: str
    options: List[str]
    user_answer: str
    correct_answer: str
    explanation: str

class QuizSubmitRequest(BaseModel):
    student_id: str = Field(default="student_001")
    topic: str
    difficulty: str = "medium"
    questions: List[UserQuestionSubmission]

class QuizQuestionResult(BaseModel):
    id: int
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str

class QuizSubmitResponse(BaseModel):
    student_id: str
    topic: str
    score: int
    total_questions: int
    accuracy: float
    updated_topic_accuracy: float
    updated_topic_strength: str
    results: List[QuizQuestionResult]

# ----------------- Progress Schemas -----------------
class TopicProgressItem(BaseModel):
    topic: str
    accuracy: float
    attempts: int
    strength: str

class ProgressResponse(BaseModel):
    student_id: str
    total_quizzes: int
    topics_practiced: int
    weak_topics: List[str]
    progress: Dict[str, TopicProgressItem]
    recommendations: List[str]

# ----------------- Ingestion Schemas -----------------
class DocumentIngestRequest(BaseModel):
    title: str
    content: str
    source_type: str = "notes"

class DocumentIngestResponse(BaseModel):
    status: str
    chunks_indexed: int
    message: str
