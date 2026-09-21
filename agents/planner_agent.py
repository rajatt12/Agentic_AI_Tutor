import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PlannerAgent:
    def __init__(self, retriever, quiz_generator, profile_manager, api_key=None, model=None):
        """Initialize Planner Agent with Groq API (via OpenAI-compatible client or Groq)"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key or "missing_key"
        )
        self.retriever = retriever
        self.quiz_generator = quiz_generator
        self.profile_manager = profile_manager
        print(f"Groq Planner Agent initialized successfully with model: {self.model}")

    def update_config(self, api_key=None, model=None):
        """Update API key or model dynamically from UI"""
        if api_key:
            self.api_key = api_key
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.api_key
            )
        if model:
            self.model = model
    
    def decide_action(self, student_id, user_query):
        """Decide what action to take based on student input"""
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            return {
                "action": "chat",
                "response": "⚠️ **Groq API Key missing**: Please enter your Groq API key in the sidebar or set `GROQ_API_KEY` in `.env` to start learning!"
            }

        intent_prompt = f"""Analyze this student query and classify the intent:
Query: "{user_query}"

Classify as ONE of:
1. EXPLANATION_REQUEST
2. QUIZ_REQUEST
3. PROGRESS_CHECK
4. GENERAL_CHAT

Reply with ONLY the exact classification name, nothing else."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intent classification system. Output only the category label."},
                    {"role": "user", "content": intent_prompt}
                ],
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip().upper()
        except Exception as e:
            return {
                "action": "chat",
                "response": f"❌ Error communicating with Groq API: {str(e)}"
            }
        
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
        
        context_text = retrieval_result.get('retrieved_content', '')
        has_context = bool(context_text.strip() and not context_text.startswith("**Source 1:** \n"))
        
        if has_context:
            explanation_prompt = f"""Based on this study material, explain the concept clearly to a student preparing for competitive exams:

Study Material:
{context_text}

Student's Question: {query}

Provide a structured, engaging, and clear explanation with examples if helpful."""
        else:
            explanation_prompt = f"""Explain the following concept clearly and thoroughly to a student preparing for competitive exams:

Student's Question: {query}

Provide a structured, engaging, and clear explanation with examples if helpful."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert tutor helping students excel in competitive exams."},
                    {"role": "user", "content": explanation_prompt}
                ],
                temperature=0.5
            )
            explanation = response.choices[0].message.content
        except Exception as e:
            explanation = f"Error generating explanation: {str(e)}"
        
        extracted_topic = self._extract_topic(query)
        quiz = self.quiz_generator.generate_quiz(
            topic=extracted_topic,
            difficulty="easy",
            num_questions=2,
            context=context_text if has_context else ""
        )
        
        return {
            "action": "explanation",
            "explanation": explanation,
            "practice_quiz": quiz,
            "plan_executed": [
                f"Identified topic: {extracted_topic}",
                "Searched study materials database" if has_context else "Applied general knowledge base",
                "Generated comprehensive explanation with Groq",
                "Created 2 adaptive practice questions"
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
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a friendly, encouraging AI tutor helping students prepare for competitive exams."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Error generating response: {str(e)}"
        
        return {
            "action": "chat",
            "response": reply
        }
    
    def _extract_topic(self, query):
        """Extract main topic from query"""
        prompt = f"Extract the main subject/topic from this query in 2-4 words: '{query}'. Reply with ONLY the topic name."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content.strip().strip('"').strip("'")
        except Exception:
            return query[:30]
