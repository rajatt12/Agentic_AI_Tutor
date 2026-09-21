import sys
import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

class QuizGeneratorAgent:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key or "missing_key"
        )
    
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

    def _call_llm(self, messages, temperature=0.3, max_tokens=1500):
        """Call Groq LLM with automatic model fallback"""
        candidate_models = [self.model, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
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
                continue
        return None
    
    def generate_quiz(self, topic, difficulty="medium", num_questions=3, context=""):
        """Generate adaptive quiz questions using Groq"""
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            return []

        context_clause = f"\nContext from study materials:\n{context}\n" if context.strip() else ""

        prompt = f"""You are an expert quiz generator for competitive exam preparation.

Create exactly {num_questions} multiple-choice questions on the topic: "{topic}".
Difficulty level: {difficulty}
{context_clause}
Return ONLY a valid JSON array matching this exact schema:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A",
    "explanation": "Brief explanation of why A is correct."
  }}
]

Requirements:
- Ensure the questions test conceptual understanding suitable for {difficulty} level.
- Options must begin with 'A) ', 'B) ', 'C) ', 'D) '.
- 'correct_answer' must be just the letter: 'A', 'B', 'C', or 'D'.
- Output strictly raw JSON, with no surrounding explanations or extra text."""
        
        content = self._call_llm(
            messages=[
                {"role": "system", "content": "You are a quiz generation expert. Output only valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        if content:
            return self._parse_json_response(content.strip())
        return []
    
    def _parse_json_response(self, content):
        """Extract and parse JSON array from LLM response"""
        try:
            # 1. Direct parse attempt
            data = json.loads(content)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "questions" in data:
                return data["questions"]
        except Exception:
            pass

        # 2. Extract JSON fenced block ```json ... ``` or [ ... ]
        json_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', content)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except Exception:
                pass
        
        # 3. Search for raw bracket-delimited array [...]
        bracket_match = re.search(r'(\[[\s\S]*\])', content)
        if bracket_match:
            try:
                return json.loads(bracket_match.group(1))
            except Exception:
                pass

        return []

    def adjust_difficulty(self, student_accuracy):
        """Adapt difficulty based on student performance"""
        if student_accuracy >= 80:
            return "hard"
        elif student_accuracy >= 50:
            return "medium"
        else:
            return "easy"
