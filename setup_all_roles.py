import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

from quality_app.models import Department, Teacher, Course, Exam, Student, User, HOD, Principal
from django.contrib.auth.hashers import make_password

print("Setting up comprehensive test data for all roles...")

# Admin
admin, created = User.objects.get_or_create(
    email='admin@test.com',
    defaults={
        'first_name': 'Super',
        'last_name': 'Admin',
        'password': make_password('password'),
        'is_staff': True,
        'is_superuser': True,
        'status': True
    }
)
if not created:
    admin.password = make_password('password')
    admin.save()
print("Admin created.")

# Principal
principal, created = Principal.objects.get_or_create(
    email='p@test.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'Principal',
        'date_of_birth': '1980-01-01',
        'gender': 'female',
        'registration_no': 'P123',
        'address': 'Campus',
        'password': make_password('password'),
        'status': True
    }
)
if not created:
    principal.password = make_password('password')
    principal.save()
print("Principal created.")

# HOD
dept, _ = Department.objects.get_or_create(name='Computer Science')
hod, created = HOD.objects.get_or_create(
    email='h@test.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'HOD',
        'date_of_birth': '1985-01-01',
        'gender': 'male',
        'registration_no': 'H123',
        'department': 'Computer Science',
        'address': 'Campus',
        'password': make_password('password'),
        'status': True
    }
)
if not created:
    hod.password = make_password('password')
    hod.save()
print("HOD created.")

print("All roles are setup with password 'password'.")
