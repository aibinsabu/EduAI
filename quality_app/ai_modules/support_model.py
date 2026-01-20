# from openai import OpenAI
# import os

# # New User Provided Key (Replacement 2)
# OPENAI_API_KEY = "AIzaSyCHYH_Uo4W1i-uOdawLpXeKmuFu2nzr5es"

# class LearningSupportBot:
#     def __init__(self):
#         try:
#             self.client = OpenAI(api_key=OPENAI_API_KEY)
#             print("Initializing Learning Support Bot (OpenAI Model Loaded)")
#         except Exception as e:
#             print(f"Error initializing OpenAI: {e}")
#             self.client = None
        
#     def get_clarification(self, query, context_text):
#         """
#         Provides clarification for a student's query using OpenAI GPT.
#         """
#         if not self.client:
#            return {
#                "answer": "AI Service not available. Please check API configuration.",
#                "relevant_section": "N/A"
#            }

#         try:
#             # Construct a prompt for RAG
#             prompt = f"""You are an intelligent teaching assistant. 
#             Answer the student's question based strictly on the provided study material context.
#             If the answer is not in the context, say so.
            
#             Context: {context_text[:4000]}... (truncated)
            
#             Student Question: {query}
            
#             Answer:"""

#             response = self.client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a helpful educational AI assistant."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 max_tokens=150,
#                 temperature=0.7
#             )
            
#             ai_answer = response.choices[0].message.content.strip()
#             citation = "Generated based on uploaded study notes."

#             return {
#                 "answer": ai_answer,
#                 "relevant_section": citation
#             }
             
#         except Exception as e:
#             print(f"OpenAI API Error: {e}")
#             return {
#                 "answer": f"I encountered an error processing your request: {str(e)}",
#                 "relevant_section": "Error"
#             }

# class SupportService:
#     _instance = None
    
#     @staticmethod
#     def get_instance():
#         if SupportService._instance is None:
#             SupportService._instance = LearningSupportBot()
#         return SupportService._instance


import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyCHYH_Uo4W1i-uOdawLpXeKmuFu2nzr5es"

class LearningSupportBot:
    def __init__(self):
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # ✅ Use correct model name for 0.8.6
            self.model = genai.GenerativeModel("models/gemini-flash-latest")
            print("Initializing Learning Support Bot (Gemini Model Loaded)")
        except Exception as e:
            print(f"Error initializing Gemini API: {e}")
            self.model = None

    def get_clarification(self, query, context_text):
        if not self.model:
            return {
                "answer": "AI Service not available. Please check API configuration.",
                "relevant_section": "N/A"
            }

        try:
            prompt = f"""
You are an intelligent teaching assistant.
Answer the student's question strictly using the provided study material.
If the answer is not present in the context, clearly say so.

Context:
{context_text[:4000]}

Student Question:
{query}

Answer:
"""
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 1000,
                    "temperature": 0.7
                }
            )

            try:
                answer_text = response.text.strip()
            except Exception:
                answer_text = "I'm sorry, I couldn't generate a complete answer. Please try again or refine your query."

            return {
                "answer": answer_text,
                "relevant_section": "Generated based on uploaded study notes."
            }

        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "answer": f"I encountered an error processing your request: {str(e)}",
                "relevant_section": "Error"
            }

class SupportService:
    _instance = None

    @staticmethod
    def get_instance():
        if SupportService._instance is None:
            SupportService._instance = LearningSupportBot()
        return SupportService._instance
