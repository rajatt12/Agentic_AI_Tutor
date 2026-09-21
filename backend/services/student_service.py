from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.models import Student, TopicPerformance, QuizAttempt, QuizQuestion

class StudentService:
    @staticmethod
    def get_or_create_student(db: Session, student_id: str, name: str = None) -> Student:
        """Fetch existing student or create a new profile in PostgreSQL"""
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            student = Student(
                student_id=student_id,
                name=name or f"Student {student_id}",
                created_at=datetime.utcnow()
            )
            db.add(student)
            db.commit()
            db.refresh(student)
        return student

    @staticmethod
    def get_topic_performance(db: Session, student_id: str, topic: str) -> TopicPerformance:
        """Retrieve student's performance on a specific topic"""
        return db.query(TopicPerformance).filter(
            TopicPerformance.student_id == student_id,
            TopicPerformance.topic == topic
        ).first()

    @staticmethod
    def update_topic_performance(db: Session, student_id: str, topic: str, accuracy: float) -> TopicPerformance:
        """Update running accuracy and strength rating for a topic"""
        StudentService.get_or_create_student(db, student_id)
        
        perf = db.query(TopicPerformance).filter(
            TopicPerformance.student_id == student_id,
            TopicPerformance.topic == topic
        ).first()

        if not perf:
            perf = TopicPerformance(
                student_id=student_id,
                topic=topic,
                accuracy=accuracy,
                attempts=1,
                strength="strong" if accuracy >= 70 else ("medium" if accuracy >= 50 else "weak"),
                updated_at=datetime.utcnow()
            )
            db.add(perf)
        else:
            perf.attempts += 1
            perf.accuracy = (
                (perf.accuracy * (perf.attempts - 1) + accuracy) / perf.attempts
            )
            if perf.accuracy >= 70:
                perf.strength = "strong"
            elif perf.accuracy >= 50:
                perf.strength = "medium"
            else:
                perf.strength = "weak"
            perf.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(perf)
        return perf

    @staticmethod
    def record_quiz_attempt(
        db: Session,
        student_id: str,
        topic: str,
        difficulty: str,
        questions_data: list
    ) -> dict:
        """Save complete quiz attempt and each question submission to PostgreSQL"""
        StudentService.get_or_create_student(db, student_id)

        total_questions = len(questions_data)
        correct_count = 0
        evaluated_questions = []

        for q in questions_data:
            chosen_letter = q.user_answer.split(")")[0].strip() if ")" in q.user_answer else q.user_answer[:1]
            correct_letter = q.correct_answer.split(")")[0].strip() if ")" in q.correct_answer else q.correct_answer[:1]
            is_correct = chosen_letter.upper() == correct_letter.upper()
            
            if is_correct:
                correct_count += 1
            
            evaluated_questions.append({
                "question": q.question,
                "options": q.options,
                "user_answer": q.user_answer,
                "correct_answer": q.correct_answer,
                "is_correct": is_correct,
                "explanation": q.explanation
            })

        accuracy = (correct_count / total_questions * 100.0) if total_questions > 0 else 0.0

        # 1. Create Quiz Attempt record
        attempt = QuizAttempt(
            student_id=student_id,
            topic=topic,
            difficulty=difficulty,
            score=correct_count,
            total_questions=total_questions,
            accuracy=accuracy,
            created_at=datetime.utcnow()
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # 2. Record each Quiz Question
        for eq in evaluated_questions:
            db_q = QuizQuestion(
                quiz_attempt_id=attempt.id,
                question=eq["question"],
                options=eq["options"],
                user_answer=eq["user_answer"],
                correct_answer=eq["correct_answer"],
                is_correct=eq["is_correct"],
                explanation=eq["explanation"]
            )
            db.add(db_q)

        # 3. Update rolling topic performance
        topic_perf = StudentService.update_topic_performance(db, student_id, topic, accuracy)
        db.commit()

        return {
            "attempt": attempt,
            "evaluated_questions": evaluated_questions,
            "topic_perf": topic_perf
        }

    @staticmethod
    def get_progress_report(db: Session, student_id: str) -> dict:
        """Compile complete student mastery metrics from PostgreSQL"""
        student = StudentService.get_or_create_student(db, student_id)
        
        topics_query = db.query(TopicPerformance).filter(
            TopicPerformance.student_id == student_id
        ).all()

        total_quizzes = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == student_id
        ).count()

        topics_dict = {}
        weak_topics = []

        for t in topics_query:
            topics_dict[t.topic] = {
                "topic": t.topic,
                "accuracy": round(t.accuracy, 1),
                "attempts": t.attempts,
                "strength": t.strength
            }
            if t.strength == "weak":
                weak_topics.append(t.topic)

        recommendations = []
        if weak_topics:
            recommendations.append(f"Focus on strengthening weak topics: {', '.join(weak_topics)}")
        elif topics_dict:
            recommendations.append("Excellent consistency! Keep taking quizzes across new topics.")
        else:
            recommendations.append("Start with your first quiz or concept explanation to track your progress!")

        return {
            "student_id": student_id,
            "total_quizzes": total_quizzes,
            "topics_practiced": len(topics_dict),
            "weak_topics": weak_topics,
            "progress": topics_dict,
            "recommendations": recommendations
        }
