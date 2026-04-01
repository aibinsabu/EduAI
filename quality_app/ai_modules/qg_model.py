from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import pdfplumber
import nltk
import random
import re

# Download tokenizer data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# ==============================
# LAZY LOAD MODEL (MEMORY EFFICIENT)
# ==============================
MODEL_NAME = "google/flan-t5-base"
_qg_pipeline = None

def get_qg_pipeline():
    global _qg_pipeline
    if _qg_pipeline is None:
        print("Loading AI model (Lazy Load)...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
            _qg_pipeline = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer
            )
            print("AI Model loaded successfully.")
        except Exception as e:
            print(f"FAILED to load AI model: {e}")
            return None
    return _qg_pipeline

# ==============================
# CLEAN TEXT UTILITY
# ==============================
def clean_text(text):
    if not text:
        return ""
    # Remove Private Use Area characters (U+E000-U+F8FF) often found in PDFs (bullet points, icons)
    cleaned = re.sub(r'[\ue000-\uf8ff]', '', text)
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

# ==============================
# EXTRACT TEXT FROM PDF
# ==============================
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_content = page.extract_text()
                if page_content:
                    text += clean_text(page_content) + " "
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()


# ==============================
# QUESTION GENERATION
# ==============================
def generate_questions(text, max_questions=5, exam_type='MCQ', difficulty='Medium', num_mcq=None, num_essay=None):
    sentences = nltk.sent_tokenize(text)
    random.shuffle(sentences)

    questions = []
    
    # Track counts for Mixed mode
    mcq_count = 0
    essay_count = 0
    
    # Default Mixed distribution if not provided
    if exam_type == 'Mixed' and (num_mcq is None or num_essay is None):
        num_mcq = max_questions // 2
        num_essay = max_questions - num_mcq

    for attempt in range(2): # Try up to 2 passes with different settings
        for sent in sentences:
            if len(questions) >= max_questions:
                break
                
            # Lenient filtering on second pass
            min_len = 50 if attempt == 0 else 30
            if len(sent) < min_len:
                continue

            qg = get_qg_pipeline()
            if qg is None:
                return questions

            # Determine current question type
            if exam_type == 'Mixed':
                if mcq_count < num_mcq:
                    current_type = 'MCQ'
                elif essay_count < num_essay:
                    current_type = 'Essay'
                else:
                    break # Reached requested counts for mixed
            else:
                current_type = exam_type

            # Adjust prompt on second pass to get different questions
            if attempt == 0:
                if current_type == 'MCQ':
                    prompt = f"generate mcq question and 4 options and correct answer from context: {sent}"
                else:
                    prompt = f"generate a descriptive theory question from context: {sent}"
            else:
                if current_type == 'MCQ':
                    prompt = f"Using a different angle, generate an MCQ question from this context: {sent}"
                else:
                    prompt = f"Explain a key concept from this text as a question: {sent}"

            try:
                output = qg(
                    prompt,
                    max_new_tokens=128,
                    do_sample=True,
                    temperature=0.7 + (attempt * 0.2), # Increase randomness on second pass
                    top_p=0.9
                )

                generated_text = output[0]["generated_text"].strip()
                if not generated_text:
                    continue

                if current_type == 'MCQ':
                    import re
                    opt_pattern = r"([A-Da-d][\)\.])\s*(.*?)(?=\s*[A-Da-d][\)\.]|$)"
                    found_opts = re.findall(opt_pattern, generated_text, re.DOTALL)
                    
                    if found_opts:
                        q_part = re.split(r"[A-Da-d][\)\.]", generated_text)[0].strip()
                        options = [opt[1].strip() for opt in found_opts]
                        while len(options) < 4:
                            options.append(f"Option {chr(65+len(options))}")
                            
                        questions.append({
                            "question": q_part if q_part else "Generated MCQ Question",
                            "answer": sent,
                            "options": options[:4],
                            "type": "MCQ"
                        })
                        mcq_count += 1
                    elif "A)" in generated_text or "a)" in generated_text or "(A)" in generated_text:
                        questions.append({
                            "question": generated_text,
                            "answer": sent,
                            "options": ["A", "B", "C", "D"],
                            "type": "MCQ"
                        })
                        mcq_count += 1
                    else:
                        # Distractor generation
                        opt_prompt = f"generate 3 wrong distractors for the answer '{sent}' based on context: {text[:500]}"
                        opt_output = qg(opt_prompt, max_new_tokens=64)
                        distractors = opt_output[0]["generated_text"].split(',')
                        
                        options = [sent] + [d.strip() for d in distractors[:3]]
                        while len(options) < 4:
                            options.append("None of the above")
                        random.shuffle(options)

                        questions.append({
                            "question": generated_text if "?" in generated_text else f"{generated_text}?",
                            "answer": sent,
                            "options": options,
                            "type": "MCQ"
                        })
                        mcq_count += 1
                else:
                    questions.append({
                        "question": generated_text if "?" in generated_text else f"{generated_text}?",
                        "answer": sent,
                        "type": "Essay" if current_type == 'Essay' else "SAQ"
                    })
                    essay_count += 1

            except Exception as e:
                print(f"Error generating question: {e}")
                continue
                
        if len(questions) >= max_questions:
            break
            
    return questions[:max_questions]

if __name__ == "__main__":
    pass
