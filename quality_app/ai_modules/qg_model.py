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
# LOAD MODEL (SAFE & STABLE)
# ==============================
print("Loading model...")

MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

qg = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer
)

print("QG Model loaded successfully (T5).")

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
def generate_questions(text, max_questions=5):
    sentences = nltk.sent_tokenize(text)
    random.shuffle(sentences)

    questions = []

    for sent in sentences:
        if len(sent) < 40:
            continue

        prompt_templates = [
            f"Generate a question based on this sentence: {sent}",
            f"Create a conceptual question from this text: {sent}",
            f"Formulate a why-type question from: {sent}",
            f"Ask a question to test understanding of: {sent}"
        ]

        prompt = random.choice(prompt_templates)

        try:
            output = qg(
                prompt,
                max_new_tokens=60,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )

            question = output[0]["generated_text"].strip()

            if len(question.split()) < 4:
                continue

            questions.append({
                "question": question,
                "answer": sent
            })

            if len(questions) >= max_questions:
                break
        except Exception as e:
            print(f"Generation Error: {e}")
            continue

    return questions

if __name__ == "__main__":
    pass
