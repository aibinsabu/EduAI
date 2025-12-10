from abc import ABC, abstractmethod
import math

# from sentence_transformers import SentenceTransformer, util

class BaseGradingModel(ABC):
    @abstractmethod
    def grade_submission(self, question, student_answer, ideal_answer, rubric=""):
        pass

class SemanticGrader(BaseGradingModel):
    def __init__(self):
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Initializing Semantic Grader (Mocked)")

    def grade_submission(self, question, student_answer, ideal_answer, rubric=""):
        """
        Grades a submission based on semantic similarity.
        Returns: { "score": float, "feedback": str }
        """
        if not student_answer:
            return {"score": 0, "feedback": "No answer provided."}

        # Mock similarity calculation
        # In prod: embedding1 = self.model.encode(student_answer)
        #          embedding2 = self.model.encode(ideal_answer)
        #          sim = util.cos_sim(embedding1, embedding2)
        
        sim = self._mock_similarity(student_answer, ideal_answer)
        
        score = round(sim * 10, 1) # Scale to 10
        
        feedback = ""
        if score > 8:
            feedback = "Excellent answer. Captures the core meaning well."
        elif score > 5:
            feedback = "Good attempt, but misses some key nuances relative to the ideal answer."
        else:
            feedback = "The answer deviates significantly from the expected response."

        return {
            "score": score,
            "feedback": feedback
        }

    def _mock_similarity(self, txt1, txt2):
        # Simple Jaccard-like similarity for mock
        set1 = set(txt1.lower().split())
        set2 = set(txt2.lower().split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

class GradingService:
    _instance = None

    @staticmethod
    def get_instance():
        if GradingService._instance is None:
            GradingService._instance = SemanticGrader()
        return GradingService._instance
