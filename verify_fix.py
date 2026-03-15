import os
import django
import sys
from unittest.mock import MagicMock, patch

# Setup Django
sys.path.append('d:/New folder (2)/project/edu')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import *
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

# Mock GradingService to avoid loading heavy models
patcher = patch('quality_app.views.GradingService')
MockGradingService = patcher.start()
mock_grader_instance = MagicMock()
mock_grader_instance.grade_submission.return_value = {"score": 10.0, "feedback": "Good job"}
MockGradingService.get_instance.return_value = mock_grader_instance

# Mock messages
patcher_msg = patch('quality_app.views.messages')
MockMessages = patcher_msg.start()

# Import view after setup
from quality_app.views import submit_exam, finalize_result

def setup_data():
    print("Setting up test data...")
    # Create Teacher
    t, _ = Teacher.objects.get_or_create(
        email="test_verifier@example.com",
        defaults={
            "first_name": "Test", "last_name": "Teacher", 
            "registration_no": "TV1", "password": "pass",
            "date_of_birth": "2000-01-01", "gender": "M", "address": "Addr"
        }
    )
    # Create Student
    s, _ = Student.objects.get_or_create(
        email="student_verifier@example.com",
        defaults={
            "first_name": "Test", "last_name": "Student", 
            "registration_no": "SV1", "password": "pass",
            "date_of_birth": "2000-01-01", "gender": "F", "address": "Addr"
        }
    )
    # Create Course & Exam
    c, _ = Course.objects.get_or_create(name="Verify Course", created_by=t)
    e, _ = Exam.objects.get_or_create(
        title="Verify Exam", 
        course=c, 
        defaults={
            "duration": 60, "date": "2025-01-01 10:00:00",
            "created_by": t
        }
    )
    # Create Question
    q, _ = Question.objects.get_or_create(
        exam=e, 
        question_text="Test Question 1", 
        defaults={"answer": "42", "question_type": "SAQ"}
    )
    
    # Clean previous results
    Result.objects.filter(exam=e, student=s).delete()
    
    return t, s, e, q

def verify_submission(student, exam, question):
    print("\n--- Testing submit_exam ---")
    factory = RequestFactory()
    
    # Prepare POST data
    data = {f"question_{question.id}": "42"}
    request = factory.post(f'/submit_exam/{exam.id}', data)
    
    # Add session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session['student_id'] = student.id
    request.session['role'] = 'student'
    request.session.save()
    
    # Call View
    response = submit_exam(request, exam.id)
    
    # Verify
    result = Result.objects.get(exam=exam, student=student)
    print(f"Result Status after submission: '{result.status}'")
    
    if result.status == 'Pending':
        print("SUCCESS: Result is Pending.")
    else:
        print(f"FAILURE: Expected 'Pending', got '{result.status}'")
        sys.exit(1)
        
    return result

def verify_teacher_finalize(teacher, result):
    print("\n--- Testing finalize_result ---")
    factory = RequestFactory()
    
    data = {"score": "100", "feedback": "Excellent work"}
    request = factory.post(f'/finalize_result/{result.id}', data)
    
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session['user_id'] = teacher.id
    request.session['role'] = 'teacher'
    request.session.save()
    
    # Call View
    response = finalize_result(request, result.id)
    
    # Verify
    result.refresh_from_db()
    print(f"Result Status after finalize: '{result.status}'")
    print(f"Score: {result.score}")
    
    if result.status == 'Released' and result.score == 100.0:
        print("SUCCESS: Result released and score updated.")
    else:
        print("FAILURE: Validation failed.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        t, s, e, q = setup_data()
        result = verify_submission(s, e, q)
        verify_teacher_finalize(t, result)
        print("\nALL TESTS PASSED.")
    except Exception as err:
        print(f"\nCRITICAL ERROR: {err}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
