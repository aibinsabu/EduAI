import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import Student, Teacher, HOD, Principal, User, Department

print("--- DEBUG REPORT ---")
print(f"Departments: {Department.objects.count()}")
for d in Department.objects.all():
    print(f" - {d.name}")

print(f"Students: {Student.objects.count()}")
for s in Student.objects.all()[:5]:
    print(f" - {s.first_name} {s.last_name} ({s.email})")

print(f"Teachers: {Teacher.objects.count()}")
print(f"HODs: {HOD.objects.count()}")
print(f"Principals: {Principal.objects.count()}")
print(f"Superusers: {User.objects.filter(is_superuser=True).count()}")
print("--- END REPORT ---")
