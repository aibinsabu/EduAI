import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import Course, Exam, Teacher

print("--- DEBUG REPORT ---")
print(f"Teachers: {Teacher.objects.count()}")
print(f"Courses: {Course.objects.count()}")
for c in Course.objects.all()[:5]:
    print(f" - {c.name} (by {c.created_by.first_name})")

print(f"Exams: {Exam.objects.count()}")
for e in Exam.objects.all()[:5]:
    print(f" - {e.title} (Status: {e.status})")

print("--- END REPORT ---")
