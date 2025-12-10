class LearningSupportBot:
    def __init__(self):
        print("Initializing Learning Support Bot")
        
    def get_clarification(self, query, context_text):
        """
        Provides clarification for a student's query based on the context.
        """
        # In prod: RAG (Retrieval Augmented Generation)
        # 1. Retrieve relevant chunks from context_text
        # 2. Feed to LLM (e.g., Llama 2 or GPT) to answer query
        
        response = f"Based on the materials provided: The concept '{query}' refers to... [Simplified Explanation based on context: {context_text[:50]}...]"
        
        return {
            "answer": response,
            "relevant_section": "Section 3.2" # citation
        }

class SupportService:
    _instance = None
    
    @staticmethod
    def get_instance():
        if SupportService._instance is None:
            SupportService._instance = LearningSupportBot()
        return SupportService._instance
