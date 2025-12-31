import os
import django
from django.core.files.base import ContentFile
import json

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import Teacher, Course, StudyMaterial, Question
from quality_app.ai_modules.qg_model import AQGService

def run_verification():
    print("--- Starting QG Verification ---")
    
    # 1. Setup Data
    try:
        # Use existing teacher if possible to avoid unique constraint issues, or create new
        teacher = Teacher.objects.first()
        if not teacher:
            print("No teacher found, creating one...")
            teacher = Teacher.objects.create(
                first_name='Test', last_name='QG', email='test_qg@example.com',
                registration_no='REG_QG_001', gender='M', date_of_birth='1990-01-01',
                password='pass', address='Address', department='CS' 
            )
        else:
            print(f"Using teacher: {teacher.first_name}")
        
        course = Course.objects.filter(created_by=teacher).first()
        if not course:
            course = Course.objects.create(name='QG 101', department='CS', created_by=teacher)
            print("Created new course")
        else:
            print(f"Using course: {course.name}")

        
        # 2. Simulate Upload & QG
        content = "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy."
        file_name = "test_note.txt"
        file_content = ContentFile(content.encode('utf-8'), name=file_name)
        
        # Create StudyMaterial
        study_material = StudyMaterial.objects.create(
            title="Test Note for QG",
            course=course,
            teacher=teacher,
            file=file_content,
            status='Approved'
        )
        print(f"Created StudyMaterial: {study_material.id}")
        
        # Trigger QG (Mimicking view logic)
        print("Triggering QG logic (mimicking views.py)...")
        aqg = AQGService.get_instance()
        questions = aqg.generate_questions(content, count=3)
        print(f"Generated {len(questions)} questions from model.")
                
        for q_data in questions:
            q = Question.objects.create(
                study_material=study_material,
                question_text=q_data.get('question'),
                question_type=q_data.get('type'),
                options=json.dumps(q_data.get('options')) if q_data.get('options') else None,
                answer=q_data.get('answer') or q_data.get('answer_key')
            )
            print(f"Saved Question ID {q.id}: {q}")
            
        # Verify
        saved_qs = Question.objects.filter(study_material=study_material)
        print(f"\nTotal Saved Questions for this material: {saved_qs.count()}")
        for sq in saved_qs:
            print(f"- Type: {sq.question_type}")
            print(f"  Question: {sq.question_text}")
            print(f"  Answer: {sq.answer}")
            if sq.options:
                print(f"  Options: {sq.options}")
            print("-" * 20)
            
        return saved_qs.count() > 0

    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if run_verification():
        print("\nSUCCESS: Verification Passed!")
    else:
        print("\nFAILURE: Verification Failed.")
