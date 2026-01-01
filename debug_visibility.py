import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import User, Course, Exam, StudyMaterial

print("-" * 30)
print("DEBUG: Checking Data for Visibility Issue")
print("-" * 30)

print("\n1. USERS (Student Role)")
students = User.objects.filter(is_superuser=False, is_staff=False) # Assuming students are just basic users
for s in students:
    print(f"Student: {s.first_name} {s.last_name} (ID: {s.id})")
    print(f" - Department: '{s.department}'") 

print("\n2. COURSES")
courses = Course.objects.all()
for c in courses:
    print(f"Course: {c.name} (ID: {c.id})")
    print(f" - Department: '{c.department}'")

print("\n3. LOGIC CHECK")
# Simulate filtering for each student
for s in students:
    if not s.department:
        print(f"WARNING: Student {s.first_name} has NO department set.")
        continue
        
    matched_courses = Course.objects.filter(department=s.department)
    print(f"Student {s.first_name} ('{s.department}') sees {matched_courses.count()} courses.")
    if matched_courses.count() == 0:
        print(f" -> POTENTIAL MISMATCH: Student has '{s.department}' but courses have: {[c.department for c in courses]}")

print("-" * 30)
