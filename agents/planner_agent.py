from openai import OpenAI
import os

class PlannerAgent:
    def __init__(self, retriever, quiz_generator, profile_manager):
        """Initialize Planner Agent with Ollama"""
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        self.retriever = retriever
        self.quiz_generator = quiz_generator
        self.profile_manager = profile_manager
        print("Ollama Planner Agent initialized successfully")
    
    def decide_action(self, student_id, user_query):
        """Decide what action to take based on student input"""
        intent_prompt = f"""Analyze this student query and classify the intent:
Query: "{user_query}"

Classify as ONE of:
1. EXPLANATION_REQUEST
2. QUIZ_REQUEST
3. PROGRESS_CHECK
4. GENERAL_CHAT

Reply with ONLY the classification name, nothing else."""
        
        response = self.client.chat.completions.create(
            model="mistral",
            messages=[{"role": "user", "content": intent_prompt}],
            temperature=0.3
        )
        
        intent = response.choices[0].message.content.strip().upper()
        
        if "EXPLANATION_REQUEST" in intent:
            return self._handle_explanation(user_query, student_id)
        elif "QUIZ_REQUEST" in intent:
            return self._handle_quiz_request(user_query, student_id)
        elif "PROGRESS_CHECK" in intent:
            return self._handle_progress_check(student_id)
        else:
            return self._handle_general_chat(user_query)
    
    def _handle_explanation(self, query, student_id):
        """Retrieve explanation and generate practice questions"""
        retrieval_result = self.retriever.retrieve_content(query)
        
        explanation_prompt = f"""Based on this study material, explain the concept clearly to a student:

Study Material:
{retrieval_result['retrieved_content']}

Student's Question: {query}

Provide a clear, concise explanation suitable for competitive exam preparation."""
        
        response = self.client.chat.completions.create(
            model="mistral",
            messages=[{"role": "user", "content": explanation_prompt}],
            temperature=0.7
        )
        
        explanation = response.choices[0].message.content
        
        extracted_topic = self._extract_topic(query)
        quiz = self.quiz_generator.generate_quiz(
            topic=extracted_topic,
            difficulty="easy",
            num_questions=2,
            context=retrieval_result['retrieved_content']
        )
        
        return {
            "action": "explanation",
            "explanation": explanation,
            "practice_quiz": quiz,
            "plan_executed": [
                f"Identified topic: {extracted_topic}",
                "Retrieved relevant study materials",
                "Generated explanation",
                "Created 2 practice questions"
            ]
        }
    
    def _handle_quiz_request(self, query, student_id):
        """Generate adaptive quiz"""
        topic = self._extract_topic(query)
        
        profile = self.profile_manager.get_progress_report(student_id)
        
        if profile and topic in profile["progress"]:
            accuracy = profile["progress"][topic]["accuracy"]
            difficulty = self.quiz_generator.adjust_difficulty(accuracy)
        else:
            difficulty = "medium"
        
        quiz = self.quiz_generator.generate_quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=5
        )
        
        return {
            "action": "quiz",
            "quiz": quiz,
            "difficulty": difficulty,
            "topic": topic
        }
    
    def _handle_progress_check(self, student_id):
        """Get student progress report"""
        report = self.profile_manager.get_progress_report(student_id)
        
        if not report:
            return {
                "action": "progress",
                "message": "No progress data available yet. Start learning to track your progress!"
            }
        
        weak_topics = report["weak_topics"]
        if weak_topics:
            recommendation = f"Focus on: {', '.join(weak_topics[:3])}"
        else:
            recommendation = "Great job! Keep practicing to maintain your strength."
        
        return {
            "action": "progress",
            "report": report,
            "recommendation": recommendation
        }
    
    def _handle_general_chat(self, query):
        """Handle general conversation"""
        response = self.client.chat.completions.create(
            model="mistral",
            messages=[
                {"role": "system", "content": "You are a friendly AI tutor helping students prepare for competitive exams."},
                {"role": "user", "content": query}
            ]
        )
        
        return {
            "action": "chat",
            "response": response.choices[0].message.content
        }
    
    def _extract_topic(self, query):
        """Extract main topic from query"""
        prompt = f"Extract the main subject/topic from this query in 2-3 words: '{query}'. Reply with ONLY the topic name."
        
        response = self.client.chat.completions.create(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
