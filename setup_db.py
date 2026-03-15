import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import Department, Teacher, Course, Exam, Student
from django.contrib.auth.hashers import make_password

print("Setting up test data...")
dept, _ = Department.objects.get_or_create(name='Computer Science')

teacher, _ = Teacher.objects.get_or_create(
    email='t@test.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'Teacher',
        'date_of_birth': '1990-01-01',
        'gender': 'male',
        'registration_no': 'T123',
        'department': 'Computer Science',
        'password': make_password('password'),
        'status': True
    }
)
teacher.password = make_password('password')
teacher.save()

course, _ = Course.objects.get_or_create(name='AI 101', created_by=teacher)

exam, _ = Exam.objects.get_or_create(
    title='Midterm AI Exam',
    course=course,
    defaults={
        'date': timezone.now(),
        'duration': 60,
        'created_by': teacher
    }
)

student, _ = Student.objects.get_or_create(
    email='s@test.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'Student',
        'date_of_birth': '2000-01-01',
        'password': make_password('password'),
        'status': True
    }
)
student.password = make_password('password')
student.save()

print(f"Test data created. Exam ID is: {exam.id}")
with open('exam_id.txt', 'w') as f:
    f.write(str(exam.id))
