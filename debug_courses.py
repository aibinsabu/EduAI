import os
import django
import sys

sys.path.append(r'D:\New folder (2)\project\edu')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import Teacher, Course, HOD

print("--- Teachers ---")
teachers = Teacher.objects.all()
for t in teachers:
    print(f"ID: {t.id}, Name: {t.first_name} {t.last_name}, Dept: {t.department}")

print("\n--- Courses ---")
courses = Course.objects.all()
for c in courses:
    creator_name = "None"
    if c.created_by:
        creator_name = f"{c.created_by.first_name} {c.created_by.last_name} (ID: {c.created_by.id})"
    print(f"ID: {c.id}, Name: {c.name}, Dept: {c.department}, Created By: {creator_name}")
