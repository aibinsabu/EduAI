from transformers import pipeline

class LearningSupportBot:
    def __init__(self):
        self.qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
        print("Initializing Learning Support Bot (Real QA Model Loaded)")
        
    def get_clarification(self, query, context_text):
        """
        Provides clarification for a student's query based on the context.
        """
        # Real RAG/QA
        # Using a QA pipeline: model="deepset/roberta-base-squad2" is good for extraction
        try:
            qa_input = {
                'question': query,
                'context': context_text
            }
            res = self.qa_pipeline(qa_input)
            # res: {'score': 0.1, 'start': 0, 'end': 0, 'answer': '...'}
            response = f"{res['answer']} (Confidence: {round(res['score'], 2)})"
            citation = f"Found in provided materials." # In advanced RAG, we would cite specific chunk
             
        except Exception as e:
            print(f"QA Model Error: {e}")
            response = "I couldn't find a specific answer in the provided text."
            citation = "N/A"

        return {
            "answer": response,
            "relevant_section": citation
        }

class SupportService:
    _instance = None
    
    @staticmethod
    def get_instance():
        if SupportService._instance is None:
            SupportService._instance = LearningSupportBot()
        return SupportService._instance
