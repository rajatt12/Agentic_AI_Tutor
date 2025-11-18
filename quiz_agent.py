import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openai import OpenAI
import json
import os

class QuizGeneratorAgent:
    def __init__(self):
        self.client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama")
    
    def generate_quiz(self, topic, difficulty="medium", num_questions=3, context=""):
        """Generate adaptive quiz questions"""
        
        prompt = f"""
You are an expert quiz generator for competitive exam preparation.

Create {num_questions} multiple-choice questions on the topic: {topic}
Difficulty level: {difficulty}

Context from study materials:
{context}

Output format (JSON only):
[
  {{
    "id": 1,
    "question": "Question text here?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A",
    "explanation": "Brief explanation of the correct answer"
  }}
]

Requirements:
- Questions should be clear and unambiguous
- All options should be plausible
- Include detailed explanations for learning
"""
        
        response = self.client.chat.completions.create(
            model="mistral",
            messages=[
                {"role": "system", "content": "You are a quiz generation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        try:
            quiz_data = json.loads(response.choices[0].message.content)
            return quiz_data
        except:
            
            return []
    
    def adjust_difficulty(self, student_accuracy):
        """Adapt difficulty based on student performance"""
        if student_accuracy >= 80:
            return "hard"
        elif student_accuracy >= 50:
            return "medium"
        else:
            return "easy"

