from abc import ABC, abstractmethod
import json
import random

# In a real environment, you would import these:
# from transformers import pipeline
# import spacy

class BaseQGModel(ABC):
    @abstractmethod
    def generate_questions(self, text, count=5, difficulty='Medium'):
        pass

class T5QuestionGenerator(BaseQGModel):
    def __init__(self):
        # self.nlp = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")
        # self.tokenizer = ...
        print("Initializing T5 Question Generator (Mocked for Demo)")

    def generate_questions(self, text, count=5, difficulty='Medium'):
        """
        Generates questions from the given text.
        difficulty: 'Easy', 'Medium', 'Hard'
        """
        # Logic to extract keywords based on difficulty
        # Easy: specific facts (Dates, Names)
        # Medium: Concepts
        # Hard: Analysis (Why, How)
        
        # Mocked response for integration testing
        generated_questions = []
        
        # Split text to simulate extraction
        sentences = text.split('.')
        clean_sentences = [s.strip() for s in sentences if len(s) > 20]
        
        for i in range(min(count, len(clean_sentences))):
            base_sentence = clean_sentences[i]
            
            # 1. MCQ
            if i % 3 == 0:
                q = {
                    "type": "MCQ",
                    "question": f"What is the primary significance of: '{base_sentence[:30]}...'?",
                    "options": [
                        "It defines the core concept.",
                        "It is irrelevant.",
                        "It contradicts the theory.",
                        "None of the above"
                    ],
                    "answer": "It defines the core concept."
                }
            # 2. Short Answer
            elif i % 3 == 1:
                q = {
                    "type": "SAQ",
                    "question": f"Explain the context of: '{base_sentence[:20]}...'",
                    "answer_key": base_sentence
                }
            # 3. Essay
            else:
                q = {
                    "type": "EBQ",
                    "question": f"Analyze the impact of the following statement: '{base_sentence}'. discuss its implications.",
                    "rubric": "Look for keywords associated with impact, analysis, and future implications."
                }
            
            generated_questions.append(q)
            
        return generated_questions

class AQGService:
    _instance = None
    
    @staticmethod
    def get_instance():
        if AQGService._instance is None:
            AQGService._instance = T5QuestionGenerator()
        return AQGService._instance
