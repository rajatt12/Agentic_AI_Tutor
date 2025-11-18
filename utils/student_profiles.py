import json
from datetime import datetime

class StudentProfileManager:
    def __init__(self):
        self.profiles = {}
    
    def create_profile(self, student_id):
        """Initialize new student profile"""
        self.profiles[student_id] = {
            "student_id": student_id,
            "topics": {},
            "quiz_history": [],
            "created_at": datetime.now().isoformat()
        }
    
    def update_topic_performance(self, student_id, topic, accuracy):
        """Update student's performance on a topic"""
        if student_id not in self.profiles:
            self.create_profile(student_id)
        
        if topic not in self.profiles[student_id]["topics"]:
            self.profiles[student_id]["topics"][topic] = {
                "accuracy": 0,
                "attempts": 0,
                "strength": "unknown"
            }
        
        topic_data = self.profiles[student_id]["topics"][topic]
        topic_data["attempts"] += 1
        topic_data["accuracy"] = (
            (topic_data["accuracy"] * (topic_data["attempts"] - 1) + accuracy) 
            / topic_data["attempts"]
        )
        
        if topic_data["accuracy"] >= 70:
            topic_data["strength"] = "strong"
        elif topic_data["accuracy"] >= 50:
            topic_data["strength"] = "medium"
        else:
            topic_data["strength"] = "weak"
    
    def get_weak_topics(self, student_id):
        """Identify topics where student needs improvement"""
        if student_id not in self.profiles:
            return []
        
        weak_topics = [
            topic for topic, data in self.profiles[student_id]["topics"].items()
            if data["strength"] == "weak"
        ]
        return weak_topics
    
    def get_progress_report(self, student_id):
        """Generate comprehensive progress report"""
        if student_id not in self.profiles:
            return None
        
        return {
            "progress": self.profiles[student_id]["topics"],
            "weak_topics": self.get_weak_topics(student_id),
            "total_quizzes": len(self.profiles[student_id]["quiz_history"])
        }
