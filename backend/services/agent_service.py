import sys
import os
from sqlalchemy.orm import Session

from backend.services.student_service import StudentService
from backend.config import settings

class AgentService:
    def __init__(self):
        self._embedding_manager = None
        self._retriever = None
        self._quiz_generator = None

    @property
    def embedding_manager(self):
        if self._embedding_manager is None:
            from utils.embeddings import EmbeddingManager
            self._embedding_manager = EmbeddingManager()
        return self._embedding_manager

    @property
    def retriever(self):
        if self._retriever is None:
            from agents.retriever_agent import RetrieverAgent
            self._retriever = RetrieverAgent()
        return self._retriever

    @property
    def quiz_generator(self):
        if self._quiz_generator is None:
            from agents.quiz_agent import QuizGeneratorAgent
            self._quiz_generator = QuizGeneratorAgent(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL
            )
        return self._quiz_generator
    
    def process_chat(self, db: Session, student_id: str, query: str, api_key: str = None, model: str = None) -> dict:
        """Execute intent classification and concept RAG generation scoped to student"""
        from agents.planner_agent import PlannerAgent
        
        key = api_key or settings.GROQ_API_KEY
        selected_model = model or settings.GROQ_MODEL
        
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
        """Generate dynamic quiz with adaptive difficulty and dual-tier context lookup"""
        key = api_key or settings.GROQ_API_KEY
        selected_model = model or settings.GROQ_MODEL
        
        self.quiz_generator.update_config(api_key=key, model=selected_model)

        if not difficulty:
            perf = StudentService.get_topic_performance(db, student_id, topic)
            if perf and perf.attempts > 0:
                difficulty = self.quiz_generator.adjust_difficulty(perf.accuracy)
            else:
                difficulty = "medium"

        retrieved = self.retriever.retrieve_content(topic, student_id=student_id)
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

    def ingest_document(self, student_id: str, title: str, content: str, is_shared: bool = False, subject: str = "General") -> int:
        """Chunk and index new study text into both ChromaDB and BM25 tagged with student_id"""
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 30]
        if not chunks:
            chunks = [content]

        metadatas = [
            {
                "title": title,
                "student_id": "global_curriculum" if is_shared else student_id,
                "is_shared": is_shared,
                "subject": subject,
                "source": "curriculum_upload" if is_shared else "student_personal_upload"
            } 
            for _ in chunks
        ]
        self.embedding_manager.add_documents(chunks, metadatas)
        return len(chunks)

    def list_student_documents(self, student_id: str) -> dict:
        """List personal notes for student along with curriculum chunks count"""
        return self.embedding_manager.get_student_documents(student_id)

agent_service = AgentService()
