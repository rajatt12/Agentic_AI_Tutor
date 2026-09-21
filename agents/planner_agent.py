import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

class PlannerAgent:
    def __init__(self, retriever, quiz_generator, profile_manager, api_key=None, model=None):
        """Initialize Planner Agent with Groq API"""
        load_dotenv(override=True)
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
        
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key or "missing_key"
        )
        self.retriever = retriever
        self.quiz_generator = quiz_generator
        self.profile_manager = profile_manager

    def update_config(self, api_key=None, model=None):
        """Update API key or model dynamically"""
        if api_key:
            self.api_key = api_key
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.api_key
            )
        if model:
            self.model = model

    def _call_llm(self, messages, temperature=0.5, max_tokens=1500):
        """Call Groq LLM with automatic model fallback"""
        candidate_models = [self.model, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
        # Deduplicate while preserving order
        unique_models = []
        for m in candidate_models:
            if m and m not in unique_models:
                unique_models.append(m)

        for mod in unique_models:
            try:
                response = self.client.chat.completions.create(
                    model=mod,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                # If model not found or rate limited, try next candidate
                continue
        return None
    
    def decide_action(self, student_id, user_query):
        """Decide what action to take based on student input"""
        load_dotenv(override=True)
        current_key = self.api_key or os.getenv("GROQ_API_KEY", "").strip()
        if not current_key or current_key == "your_groq_api_key_here":
            return {
                "action": "chat",
                "response": "Hello! I am ready to help you learn. Please ensure your learning engine credentials are configured to start studying."
            }

        # Refresh client with active key if needed
        if current_key != self.client.api_key:
            self.api_key = current_key
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.api_key
            )

        intent_prompt = f"""Analyze this student query and classify the intent:
Query: "{user_query}"

Classify as ONE of:
1. EXPLANATION_REQUEST
2. QUIZ_REQUEST
3. PROGRESS_CHECK
4. GENERAL_CHAT

Reply with ONLY the exact classification name, nothing else."""
        
        intent_resp = self._call_llm(
            messages=[
                {"role": "system", "content": "You are an intent classification system. Output only the category label."},
                {"role": "user", "content": intent_prompt}
            ],
            temperature=0.1,
            max_tokens=20
        )
        
        intent = (intent_resp or "").strip().upper()
        
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

        explanation = self._call_llm(
            messages=[
                {"role": "system", "content": "You are an expert tutor helping students excel in competitive exams."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.5,
            max_tokens=1200
        )

        if not explanation:
            explanation = f"I'm here to help you master this concept! Let's explore '{query}'. Could you specify which part of this topic you'd like to dive into?"
        
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
            "topic": extracted_topic
        }
    
    def _handle_quiz_request(self, query, student_id):
        """Generate adaptive quiz"""
        topic = self._extract_topic(query)
        
        profile = self.profile_manager.get_progress_report(student_id)
        
        if profile and topic in profile.get("progress", {}):
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
        
        if not report or not report.get("progress"):
            return {
                "action": "progress",
                "message": "You don't have any recorded quiz attempts yet. Complete a quiz to see your mastery metrics!"
            }
        
        weak_topics = report.get("weak_topics", [])
        if weak_topics:
            recommendation = f"We recommend focusing on: {', '.join(weak_topics[:3])}"
        else:
            recommendation = "Great job! Keep practicing across your topics to maintain mastery."
        
        return {
            "action": "progress",
            "report": report,
            "recommendation": recommendation
        }
    
    def _handle_general_chat(self, query):
        """Handle general conversation"""
        reply = self._call_llm(
            messages=[
                {"role": "system", "content": "You are a friendly, encouraging AI tutor helping students prepare for competitive exams."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=600
        )
        if not reply:
            reply = "I am here to help you study and prepare for your exams. Ask me any question or concept!"
        
        return {
            "action": "chat",
            "response": reply
        }
    
    def _extract_topic(self, query):
        """Extract main topic from query"""
        prompt = f"Extract the main subject/topic from this query in 2-4 words: '{query}'. Reply with ONLY the topic name."
        
        extracted = self._call_llm(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=20
        )
        if extracted:
            return extracted.strip().strip('"').strip("'")
        return query[:30]
