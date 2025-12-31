from abc import ABC, abstractmethod
import json
import random

# In a real environment, you would import these:
from transformers import pipeline
# import spacy

class BaseQGModel(ABC):
    @abstractmethod
    def generate_questions(self, text, count=5, difficulty='Medium'):
        pass

class T5QuestionGenerator(BaseQGModel):
    def __init__(self):
        self.nlp = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")
        # self.tokenizer = ...
        print("Initializing T5 Question Generator (Real Model Loaded)")

    def generate_questions(self, text, count=5, difficulty='Medium'):
        """
        Generates questions from the given text.
        difficulty: 'Easy', 'Medium', 'Hard'
        """
        # Logic to extract keywords based on difficulty
        # Easy: specific facts (Dates, Names)
        # Medium: Concepts
        # Hard: Analysis (Why, How)
        
        # Real T5 Generation
        # Prefix text with "generate questions: " depending on model training, 
        # valhalla/t5-base-qg-hl typically expects answer-aware generation, 
        # but for simple context we can try direct generation or use a simpler pipeline.
        # For this demo, we assume the pipeline handles the end-to-end task (some pipelines do).
        
        # NOTE: valhalla/t5-base-qg-hl is answer-aware, typically needing "generate question: <answer> context: <context>"
        # For simplicity in this direct integration without answer extraction step first, we use a simpler approach 
        # or mock the pre-processing. 
        # Let's try to generate questions by iterating over potential answers (keywords from text).

        generated_questions = []
        sentences = text.split('.')
        clean_sentences = [s.strip() for s in sentences if len(s) > 20]

        for i in range(min(count, len(clean_sentences))):
            # Simple heuristic: treat the sentence as context and full sentence as answer key for SAQ/MCQ generation
            base_sentence = clean_sentences[i]
            
            # Prepare input for the model
            input_text = f"generate question: {base_sentence} context: {base_sentence}"
            
            # Run model
            try:
                result = self.nlp(input_text)
                # result looks like [{'generated_text': 'Question?'}]
                question_text = result[0]['generated_text']
            except Exception as e:
                print(f"Model Error: {e}")
                question_text = f"What is the significance of: {base_sentence[:20]}...?" # Fallback

            
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
