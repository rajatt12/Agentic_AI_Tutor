import sys
import os
from sqlalchemy.orm import Session

from agents.planner_agent import PlannerAgent
from agents.retriever_agent import RetrieverAgent
from agents.quiz_agent import QuizGeneratorAgent
from utils.embeddings import EmbeddingManager
from backend.services.student_service import StudentService
from backend.config import settings

class AgentService:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.retriever = RetrieverAgent()
        self.quiz_generator = QuizGeneratorAgent(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL
        )
    
    def process_chat(self, db: Session, student_id: str, query: str, api_key: str = None, model: str = None) -> dict:
        """Execute intent classification and concept RAG generation"""
        key = api_key or settings.GROQ_API_KEY
        selected_model = model or settings.GROQ_MODEL
        
        # Build profile adapter for PlannerAgent
        class PostgresProfileAdapter:
            def get_progress_report(self, sid):
                return StudentService.get_progress_report(db, sid)

        planner = PlannerAgent(
            retriever=self.retriever,
            quiz_generator=self.quiz_generator,
            profile_manager=PostgresProfileAdapter(),
            api_key=key,
            model=selected_model
        )
        
        return planner.decide_action(student_id, query)

    def generate_adaptive_quiz(
        self,
        db: Session,
        student_id: str,
        topic: str,
        num_questions: int = 3,
        difficulty: str = None,
        api_key: str = None,
        model: str = None
    ) -> dict:
        """Generate dynamic quiz with adaptive difficulty looked up from PostgreSQL"""
        key = api_key or settings.GROQ_API_KEY
        selected_model = model or settings.GROQ_MODEL
        
        self.quiz_generator.update_config(api_key=key, model=selected_model)

        if not difficulty:
            perf = StudentService.get_topic_performance(db, student_id, topic)
            if perf and perf.attempts > 0:
                difficulty = self.quiz_generator.adjust_difficulty(perf.accuracy)
            else:
                difficulty = "medium"

        # Search for any relevant study notes as context for richer questions
        retrieved = self.retriever.retrieve_content(topic)
        context = retrieved.get("retrieved_content", "")

        questions = self.quiz_generator.generate_quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            context=context
        )

        return {
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions
        }

    def ingest_document(self, title: str, content: str) -> int:
        """Chunk and index new study text into both ChromaDB and BM25"""
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 30]
        if not chunks:
            chunks = [content]

        metadatas = [{"title": title, "source": "user_upload"} for _ in chunks]
        self.embedding_manager.add_documents(chunks, metadatas)
        return len(chunks)

agent_service = AgentService()
