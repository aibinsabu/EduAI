from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import *

# Create your views here.
def home(request):
    return render(request,"home.html")

def index(request):
    return render(request,"index.html")

def register(request):
    if request.method == "POST":
        profile = request.FILES.get('profile')
        username = request.POST.get('username')
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # result = User.objects.create(profile=profile, username=username, fullname=fullname, 	email=email, password=make_password(password))
        # result.save()
    return render(request, 'register.html')



def about(request):
    return render(request, 'about.html')

def service(request):
    return render(request, 'service.html')

def project(request):
    return render(request, 'project.html')

def team(request):
    return render(request, 'team.html')

def testimonial(request):
    return render(request, 'testimonial.html')

def page_not_found(request):
    return render(request, '404.html')

def principle_registration(request):
    if request.method == "POST":
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        registration_no = request.POST.get('registration_no')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('principle_registration')

        if Principal.objects.filter(email=email).exists():
            messages.error(request, "A principal with this email already exists.")
            return redirect('principle_registration')
        
        elif User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('principle_registration')
        
        elif HOD.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('principle_registration')
        
        elif Teacher.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('principle_registration')
        
        if Principal.objects.filter(registration_no=registration_no).exists():
            messages.error(request, "A principal with this registration number already exists.")
            return redirect('principle_registration')

        Principal.objects.create(
            first_name=firstname,
            last_name=lastname,
            email=email,
            date_of_birth=dob,
            gender=gender,
            registration_no=registration_no,
            address=address,
            password=make_password(password)
        )
        messages.success(request, "Registration successful.")
        return redirect('index')

    return render(request, 'principle-registration.html')


def hod_registration(request):
    if request.method == "POST":
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        registration_no = request.POST.get('registration_no')
        department = request.POST.get('department')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('hod_registration')

        if HOD.objects.filter(email=email).exists():
            messages.error(request, "An HOD with this email already exists.")
            return redirect('hod_registration')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('hod_registration')
        elif Principal.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('hod_registration')
        elif Teacher.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('hod_registration')
        
        if HOD.objects.filter(registration_no=registration_no).exists():
            messages.error(request, "An HOD with this registration number already exists.")
            return redirect('hod_registration')

        HOD.objects.create(
            first_name=firstname,
            last_name=lastname,
            email=email,
            date_of_birth=dob,
            gender=gender,
            registration_no=registration_no,
            department=department,
            address=address,
            password=make_password(password)
        )
        messages.success(request, "Registration successful.")
        return redirect('index')

    return render(request, 'hod-registration.html')


def teacher_registration(request):
    if request.method == "POST":
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        registration_no = request.POST.get('registration_no')
        department = request.POST.get('department')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('teacher_registration')

        if Teacher.objects.filter(email=email).exists():
            messages.error(request, "A teacher with this email already exists.")
            return redirect('teacher_registration')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('teacher_registration')
        elif Principal.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('teacher_registration')
        elif HOD.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('teacher_registration')

        if Teacher.objects.filter(registration_no=registration_no).exists():
            messages.error(request, "A teacher with this registration number already exists.")
            return redirect('teacher_registration')

        Teacher.objects.create(
            first_name=firstname,
            last_name=lastname,
            email=email,
            date_of_birth=dob,
            gender=gender,
            registration_no=registration_no,
            department=department,
            address=address,
            password=make_password(password)
        )
        messages.success(request, "Registration successful.")
        return redirect('index')

    return render(request, 'teacher-registration.html')


def student_registration(request):
    if request.method == "POST":
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        registration_no = request.POST.get('registration_no')
        department = request.POST.get('department')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('student_registration')

        # Prevent duplicate email
        if User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('student_registration')
        elif Principal.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('student_registration')
        elif HOD.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('student_registration')
        elif Teacher.objects.filter(email=email).exists():
            messages.error(request, "An User with this email already exists.")
            return redirect('student_registration')
        
        if User.objects.filter(registration_no=registration_no).exists():
            messages.error(request, "A student with this registration number already exists.")
            return redirect('student_registration')
        # Create user and set password properly
        user = User(
            first_name=firstname,
            last_name=lastname,
            email=email,
            date_of_birth=dob,
            gender=gender,
            registration_no=registration_no,
            department=department,
            address=address,
        )
        user.set_password(password)
        user.save()
        messages.success(request, "Registration successful.")
        return redirect('index')

    return render(request, 'student-registration.html')
