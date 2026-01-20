from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer, util

class BaseGradingModel(ABC):
    @abstractmethod
    def grade_submission(self, question, student_answer, ideal_answer, rubric=""):
        pass

class GradingService(BaseGradingModel):
    def __init__(self):
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu', model_kwargs={"low_cpu_mem_usage": False})
            print("Initializing Grading Service (Real Model Loaded)")
        except Exception as e:
            print(f"Error initializing Grading Model: {e}")
            self.model = None

    def grade_submission(self, question, student_answer, ideal_answer, rubric=""):
        if not student_answer.strip():
            return {"score": 0, "feedback": "No answer provided."}
            
        if not self.model:
            return {"score": 0, "feedback": "Grading Service Unavailable."}

        embedding1 = self.model.encode(student_answer, convert_to_tensor=True)
        embedding2 = self.model.encode(ideal_answer, convert_to_tensor=True)

        sim = float(util.cos_sim(embedding1, embedding2)[0][0])

        if sim >= 0.85:
            score = 10
            feedback = "Excellent answer. Very close to the expected answer."
        elif sim >= 0.70:
            score = 8
            feedback = "Very good answer, minor details missing."
        elif sim >= 0.55:
            score = 6
            feedback = "Good attempt but lacks depth."
        elif sim >= 0.40:
            score = 4
            feedback = "Partially correct but important points missing."
        elif sim >= 0.25:
            score = 2
            feedback = "Very weak answer."
        else:
            score = 0
            feedback = "Incorrect answer."

        return {
            "score": score,
            "similarity": round(sim, 3),
            "feedback": feedback
        }
