from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from quality_app.models import *
from quality_app.views import submit_exam, finalize_result
import sys, os

# Mocking
patcher = patch('quality_app.views.GradingService')
MockGradingService = patcher.start()
mock_grader = MagicMock()
mock_grader.grade_submission.return_value = {"score": 10.0, "feedback": "Good job"}
MockGradingService.get_instance.return_value = mock_grader

# Mock ProctoringService to avoid it trying to load things if imported
patcher_proc = patch('quality_app.views.ProctoringService')
MockProctoringService = patcher_proc.start()
MockProctoringService.get_instance.return_value = MagicMock()


patcher_msg = patch('quality_app.views.messages')
MockMessages = patcher_msg.start()

# Data Setup
print("Setting up data...")
t, _ = Teacher.objects.get_or_create(email="v_teach@test.com", defaults={"first_name": "T", "last_name": "T", "registration_no": "VT1", "password": "x", "date_of_birth": "2000-01-01", "gender": "M", "address": "x"})
s, _ = Student.objects.get_or_create(email="v_stud@test.com", defaults={"first_name": "S", "last_name": "S", "registration_no": "VS1", "password": "x", "date_of_birth": "2000-01-01", "gender": "F", "address": "x"})
c, _ = Course.objects.get_or_create(name="V Course", created_by=t)
e, _ = Exam.objects.get_or_create(title="V Exam", course=c, defaults={"duration": 60, "date": "2024-01-01", "created_by": t})
q, _ = Question.objects.get_or_create(exam=e, question_text="Q1", defaults={"answer": "A", "question_type": "SAQ"})

Result.objects.filter(exam=e, student=s).delete()

# Test Submit
print("Testing Submit...")
factory = RequestFactory()
req = factory.post(f'/submit_exam/{e.id}', {f"question_{q.id}": "A"})
mid = SessionMiddleware(lambda x: None)
mid.process_request(req)
req.session['student_id'] = s.id
req.session['role'] = 'student'
req.session.save()

submit_exam(req, e.id)
r = Result.objects.get(exam=e, student=s)
print(f"Expected Pending, got {r.status}")
if r.status != 'Pending':
    print(f"FAIL STATUS CHECK 1")
else:
    print(f"PASS STATUS CHECK 1")

# Test Finalize
print("Testing Finalize...")
req2 = factory.post(f'/finalize_result/{r.id}', {'score': 100, 'feedback': 'Good'})
mid.process_request(req2)
req2.session['user_id'] = t.id
req2.session['role'] = 'teacher'
req2.session.save()

finalize_result(req2, r.id)
r.refresh_from_db()

print(f"Expected Released, got {r.status}")
if r.status == 'Released' and r.score == 100:
    print(f"PASS STATUS CHECK 2")
else:
    print(f"FAIL STATUS CHECK 2")
