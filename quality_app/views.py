from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from .ai_modules import (
    generate_questions,
    extract_text_from_pdf,
    GradingService,
    SupportService,
    ProctoringService
)
import json

# ---------------------------------------------------
# GLOBAL PROCTORING INSTANCE
# ---------------------------------------------------
# proctoring_engine = ProctoringService.get_instance() # Moved to lazy load in proctoring_stream


# Create your views here.
def home(request):
    return render(request,"index.html")

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

def hod_dashboard(request):
    return render(request, 'hod_dashboard.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check Admin(Superuser) in User table
        try:
            user = User.objects.get(email=email)
            if user.is_superuser and user.check_password(password):
                auth_login(request, user)
                request.session["role"] = "admin"
                return redirect("admin_dashboard")
        except User.DoesNotExist:
            pass

        # Check Student Table
        try:
            student = Student.objects.get(email=email)
            if check_password(password, student.password):
                request.session["role"] = "student"
                request.session["student_id"] = student.id
                return redirect("student_dashboard")
        except Student.DoesNotExist:
            pass

        # Check Other Roles
        for model, role in [(Teacher, "teacher"), (HOD, "hod"), (Principal, "principal")]:
            try:
                obj = model.objects.get(email=email)
                if check_password(password, obj.password):
                    request.session["role"] = role
                    request.session["user_id"] = obj.id
                    request.session["user_name"] = f"{obj.first_name} {obj.last_name}"
                    return redirect(f"{role}_dashboard")
            except model.DoesNotExist:
                pass

        messages.error(request, "Invalid credentials")
    return render(request, "login.html")


def logout(request):
    auth_logout(request)
    request.session.flush()
    return redirect("login")

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
        return redirect('principal_dashboard')

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
        return redirect('hod_dashboard')

    departments = Department.objects.all()
    return render(request, 'hod-registration.html', {'departments': departments})


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

    departments = Department.objects.all()
    return render(request, 'teacher-registration.html', {'departments': departments})


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
        if Student.objects.filter(email=email).exists():
            messages.error(request, "A student with this email already exists.")
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
        
        if Student.objects.filter(registration_no=registration_no).exists():
            messages.error(request, "A student with this registration number already exists.")
            return redirect('student_registration')
        
        # Create student and set password properly
        student = Student(
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
        student.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    departments = Department.objects.all()
    return render(request, 'student-registration.html', {'departments': departments})


# --- Teacher Dashboard Views ---

def teacher_dashboard(request):
    # Ensure user is a teacher
    if not request.session.get('role') == 'teacher':
        messages.error(request, "Access denied. Teacher only.")
        return redirect('login')

    teacher_id = request.session.get('user_id')
    teacher = Teacher.objects.get(id=teacher_id)
    
    # Context Data
    courses = Course.objects.filter(created_by=teacher)
    exams_count = Exam.objects.filter(course__in=courses).count()
    pending_results = Result.objects.filter(exam__course__in=courses, status='Pending').count()
    
    context = {
        'teacher': teacher,
        'courses_count': courses.count(),
        'exams_count': exams_count,
        'pending_results': pending_results,
    }
    return render(request, 'teacher_dashboard.html', context)

def teacher_courses(request):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
    
    teacher_id = request.session.get('user_id')
    teacher = Teacher.objects.get(id=teacher_id)
    courses = Course.objects.filter(created_by=teacher)
    departments = Department.objects.all()
    
    return render(request, 'teacher_courses.html', {'courses': courses, 'teacher': teacher, 'departments': departments})

def create_course(request):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        
        teacher_id = request.session.get('user_id')
        teacher = Teacher.objects.get(id=teacher_id)
        
        Course.objects.create(
            name=name,
            department=department,
            created_by=teacher
        )
        messages.success(request, "Course created successfully.")
        return redirect('teacher_courses')
    
    return redirect('teacher_courses')

def upload_material(request):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        course_id = request.POST.get('course_id')
        file = request.FILES.get('file')
        
        teacher_id = request.session.get('user_id')
        teacher = Teacher.objects.get(id=teacher_id)
        course = Course.objects.get(id=course_id)
        
        study_material = StudyMaterial.objects.create(
            title=title,
            course=course,
            teacher=teacher,
            file=file,
            status='Approved'
        )
        
        # Trigger Question Generation
        try:
            if file:
                content = ""
                file_ext = file.name.split('.')[-1].lower()

                if file_ext == 'txt':
                    study_material.file.open('r')
                    content = study_material.file.read()
                    if isinstance(content, bytes):
                        content = content.decode('utf-8')
                    study_material.file.close()

                elif file_ext == 'pdf':
                    # Save temporarily to disk to read if needed by external lib or use BytesIO if library supports it
                    # extract_text_from_pdf in qg_model uses pdfplumber.open(path).
                    # Since we are using FileField, the file might be in memory or temp file.
                    # We need the absolute path.
                    try:
                        content = extract_text_from_pdf(study_material.file.path)
                    except Exception as pdf_err:
                        print(f"PDF extraction error: {pdf_err}")
                        content = ""

                if content:
                    # aqg = AQGService.get_instance()
                    questions = generate_questions(content, max_questions=5)
                    
                    for q_data in questions:
                        Question.objects.create(
                            study_material=study_material,
                            question_text=q_data.get('question'),
                            question_type='SAQ', # Defaulting to SAQ as new model returns text/answer pairs
                            # options=json.dumps(q_data.get('options')) if q_data.get('options') else None,
                            answer=q_data.get('answer')
                        )
                    messages.success(request, "Material uploaded and questions generated successfully.")
                else:
                    messages.warning(request, "Material uploaded but could not extract text for QG (Empty or unsupported format).")
            else:
                messages.warning(request, "Material uploaded but file handling failed.")
        except Exception as e:
            print(f"Error generating questions: {e}")
            messages.warning(request, f"Material uploaded, but question generation failed: {e}")

        return redirect('teacher_courses')
        
    return redirect('teacher_courses') # Should be accessed via POST from modal

def teacher_exams(request):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    teacher_id = request.session.get('user_id')
    teacher = Teacher.objects.get(id=teacher_id)
    
    # Filter exams created by this teacher or for their courses
    courses = Course.objects.filter(created_by=teacher)
    exams = Exam.objects.filter(course__in=courses).order_by('-created_at')
    
    return render(request, 'teacher_exams.html', {'exams': exams, 'courses': courses})

import json

def create_exam(request):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        course_id = request.POST.get('course_id')
        date = request.POST.get('date')
        duration = request.POST.get('duration')
        exam_type = request.POST.get('exam_type')
        difficulty = request.POST.get('difficulty')
        
        # Proctoring Settings
        camera = request.POST.get('camera') == 'on'
        screen = request.POST.get('screen') == 'on'
        audio = request.POST.get('audio') == 'on'
        proctoring_config = {
            'camera': camera,
            'screen': screen,
            'audio': audio
        }
        
        teacher_id = request.session.get('user_id')
        teacher = Teacher.objects.get(id=teacher_id)
        course = Course.objects.get(id=course_id)
        
        # AI Question Generation Trigger
        # If 'AI' is selected in creation method (assuming we add a field or checkbox for it, or infer from context)
        # For this demo, let's assume we want to generate questions if specific params are present or just demonstrate the call.
        
        # NOTE: In a real flow, you might want to generate questions BEFORE creating the Exam object
        # or store them in a JSON field on the Exam.
        
        generated_questions_data = {}
        if request.POST.get('creation_method') == 'AI' or True: # Force AI for demo if needed, or check a flag
             # Fetch course material (simplification: just taking the course name/desc as text context for now)
             # In reality, you'd fetch StudyMaterial.objects.filter(course=course).first().file.read()
             # Fetch course material (text aggregation)
             context_text = f"Content for course {course.name}. "
             
             materials = StudyMaterial.objects.filter(course=course)
             for m in materials:
                 try:
                     f_ext = m.file.name.split('.')[-1].lower()
                     if f_ext == 'txt':
                        with open(m.file.path, 'r', encoding='utf-8') as f:
                            context_text += f.read() + " "
                     elif f_ext == 'pdf':
                        context_text += extract_text_from_pdf(m.file.path) + " "
                 except Exception as e:
                     print(f"Error reading material {m.id}: {e}")
             
             if len(context_text) < 50:
                 # Fallback if no content found
                 context_text += " ".join([m.title for m in materials])
             
             num_questions = int(request.POST.get('num_questions', 5))
             # aqg = AQGService.get_instance()
             questions = generate_questions(context_text, max_questions=num_questions)
             # Store these questions somewhere. For now, we'll put them in a JSON field if Exam had one, 
             # or just log them. Let's assume Exam model has a 'questions_data' field or we create Question objects.
             # Since Question model isn't in the provided models.py, I'll serialize them to a potential new field 
             # or just print/log for the integration proof.
             print(f"DEBUG: AI Generated Questions: {questions}")
             generated_questions_data = questions

        exam = Exam.objects.create(
            title=title,
            course=course,
            date=date,
            duration=duration,
            exam_type=exam_type,
            difficulty=difficulty,
            proctoring_config=json.dumps(proctoring_config),
            creation_method='AI', # Explicitly marking as AI for dashboard stats
            created_by=teacher,
            status='Scheduled'
        )
        
        if generated_questions_data:
            for q_data in generated_questions_data:
                Question.objects.create(
                    exam=exam,
                    question_text=q_data.get('question'),
                    question_type='SAQ', # Default or infer
                    answer=q_data.get('answer')
                )

        
        messages.success(request, "Exam created and scheduled successfully.")
        return redirect('teacher_exams')
        
    return redirect('teacher_exams')

def teacher_results(request):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    teacher_id = request.session.get('user_id')
    teacher = Teacher.objects.get(id=teacher_id)
    courses = Course.objects.filter(created_by=teacher)
    
    # Get all pending results for these courses
    # Assuming Result is linked to Exam which is linked to Course
    pending_results = Result.objects.filter(exam__course__in=courses, status='Pending')
    
    return render(request, 'teacher_results.html', {'results': pending_results})

def result_detail(request, result_id):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    result = Result.objects.get(id=result_id)
    return render(request, 'teacher_result_detail.html', {'result': result})

def finalize_result(request, result_id):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback')
        
        result = Result.objects.get(id=result_id)
        result.score = score
        result.ai_feedback = feedback # Override or append
        result.status = 'Released' # Or 'Graded'
        result.save()
        
        messages.success(request, "Result finalized and released.")
        return redirect('teacher_results')
    
    return redirect('teacher_results')

def delete_exam(request, exam_id):
    if not request.session.get('role') == 'teacher':
        return redirect('login')
        
    try:
        exam = Exam.objects.get(id=exam_id)
        # Verify ownership (optional but good security)
        # if exam.course.created_by.id != request.session.get('user_id'):
             # messages.error(request, "Permission denied.")
             # return redirect('teacher_dashboard')
             
        exam.delete()
        messages.success(request, "Exam deleted successfully.")
    except Exam.DoesNotExist:
        messages.error(request, "Exam not found.")
    except Exception as e:
        messages.error(request, f"Error deleting exam: {str(e)}")
        
    return redirect('teacher_exams')

# --- Principal Dashboard Views ---

from django.db.models import Count, Avg, Q
from django.utils import timezone

def principal_dashboard(request):
    # Ensure user is a principal
    if not request.session.get('role') == 'principal':
        messages.error(request, "Access denied. Principal only.")
        return redirect('login')

    principal_id = request.session.get('user_id')
    principal = Principal.objects.get(id=principal_id)

    # 1. Institutional Overview
    total_students = User.objects.count()
    active_teachers = Teacher.objects.filter(status=True).count()
    total_exams = Exam.objects.count()

    # 2. Departmental Performance
    # Aggregate data by department
    departments = Teacher.objects.values_list('department', flat=True).distinct()
    dept_performance = []
    
    for dept in departments:
        if dept:
            # Get teachers in this dept
            teachers = Teacher.objects.filter(department=dept)
            courses = Course.objects.filter(created_by__in=teachers)
            exams = Exam.objects.filter(course__in=courses)
            results = Result.objects.filter(exam__in=exams)
            
            avg_score = results.aggregate(Avg('score'))['score__avg'] or 0
            
            # Calculate pass percentage
            total_results = results.count()
            passed_results = results.filter(is_pass=True).count()
            pass_percentage = (passed_results / total_results * 100) if total_results > 0 else 0
            
            dept_performance.append({
                'name': dept,
                'avg_score': round(avg_score, 2),
                'pass_percentage': round(pass_percentage, 2),
                'course_completion': 85 # Placeholder methodology
            })

    # 3. AI Efficacy Index
    ai_exams = Exam.objects.filter(creation_method='AI').count()
    manual_exams = Exam.objects.filter(creation_method='Manual').count()
    total_created_exams = ai_exams + manual_exams
    ai_adoption_ratio = (ai_exams / total_created_exams * 100) if total_created_exams > 0 else 0
    
    # Overridden grades: where AI feedback exists but score might be adjusted (heuristic)
    # For now, we count specific flag or assumption. Let's assume passed with very high score but low AI confidence if we had that.
    # We will use a placeholder query for "Overridden" based on logic: status='Released' and ai_feedback is not empty
    overridden_grades = Result.objects.filter(status='Released').exclude(ai_feedback='').count() 

    # 4. System Integrity & Security
    proctoring_anomalies = ProctoringLog.objects.values('flag_type').annotate(count=Count('id'))
    
    # Recent Auth Logs (User creations)
    recent_users = User.objects.order_by('-created_at')[:5]
    
    # Faculty Approval Queue
    pending_teachers = Teacher.objects.filter(status=False)
    pending_teachers_count = pending_teachers.count()

    context = {
        'principal': principal,
        'total_students': total_students,
        'active_teachers': active_teachers,
        'total_exams': total_exams,
        'dept_performance': dept_performance, # For charts
        'ai_stats': {
            'adoption_ratio': round(ai_adoption_ratio, 1),
            'ai_exams': ai_exams,
            'manual_exams': manual_exams,
            'overridden_grades': overridden_grades
        },
        'proctoring_anomalies': list(proctoring_anomalies),
        'recent_users': recent_users,
        'pending_teachers': pending_teachers,
        'pending_teachers_count': pending_teachers_count,
    }

    print("DEBUG: AI Stats:", context['ai_stats'])
    print("DEBUG: Proctoring Anomalies:", context['proctoring_anomalies'])
    print("DEBUG: Pending Teachers Count:", context['pending_teachers_count'])
    print("DEBUG: Pending Teachers:", list(pending_teachers))

    return render(request, 'principal_dashboard.html', context)

def approve_teacher(request, teacher_id):
    if not (request.session.get('role') == 'principal' or request.user.is_superuser):
        return redirect('login')
        
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.status = True
        teacher.save()
        messages.success(request, f"Teacher {teacher.first_name} approved successfully.")
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher not found.")
        
    if request.user.is_superuser:
        return redirect('admin_user_list', role='teacher')
    return redirect('principal_dashboard')

def reject_teacher(request, teacher_id):
    if not (request.session.get('role') == 'principal' or request.user.is_superuser):
        return redirect('login')
        
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.delete() 
        messages.success(request, f"Teacher {teacher.first_name} rejected.")
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher not found.")
        
    if request.user.is_superuser:
        return redirect('admin_user_list', role='teacher')
    return redirect('principal_dashboard')
        
    return redirect('principal_dashboard')

def principal_student_list(request):
    if not request.session.get('role') == 'principal':
        return redirect('login')
        
    students = User.objects.all().order_by('first_name')
    return render(request, 'principal_student_list.html', {'students': students})

def principal_teacher_list(request):
    if not request.session.get('role') == 'principal':
        return redirect('login')
        
    teachers = Teacher.objects.all().order_by('first_name')
    return render(request, 'principal_teacher_list.html', {'teachers': teachers})

def principal_edit_teacher(request, teacher_id):
    if not request.session.get('role') == 'principal':
        return redirect('login')
        
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        if request.method == 'POST':
            teacher.department = request.POST.get('department')
            teacher.designation = request.POST.get('designation')
            teacher.save()
            messages.success(request, f"Details for {teacher.first_name} updated successfully.")
            return redirect('principal_teacher_list')
            
        return render(request, 'principal_edit_teacher.html', {'teacher': teacher})
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher not found.")
        return redirect('principal_teacher_list')

    except Teacher.DoesNotExist:
        messages.error(request, "Teacher not found.")
        return redirect('principal_teacher_list')

def generate_principal_report(request):
    if not request.session.get('role') == 'principal':
        return redirect('login')

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        messages.error(request, "Report generation library not installed.")
        return redirect('principal_dashboard')

    principal_id = request.session.get('user_id')
    principal = Principal.objects.get(id=principal_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="principal_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"Institution Performance Report", styles['Title']))
    elements.append(Paragraph(f"Generated by: {principal.first_name} {principal.last_name}", styles['Normal']))
    elements.append(Paragraph(f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # 1. Overview Stats
    total_students = User.objects.count()
    active_teachers = Teacher.objects.filter(status=True).count()

    # ... (Rest of report generation logic would be here, assuming it continues)
    # Since I cannot see the end of the file, I will append the new views after this block if this was the end, 
    # but I should validly append to the true end of the file. 
    # To be safe, I will read the end of the file first.
    total_exams = Exam.objects.count()
    
    data = [
        ['Metric', 'Count'],
        ['Total Students', str(total_students)],
        ['Active Teachers', str(active_teachers)],
        ['Total Exams Administered', str(total_exams)],
    ]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(Paragraph("Overview", styles['Heading2']))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # 2. Department Performances
    elements.append(Paragraph("Departmental Performance", styles['Heading2']))
    dept_data = [['Department', 'Avg Score', 'Pass Rate']]
    
    departments = Teacher.objects.values_list('department', flat=True).distinct()
    for dept in departments:
        if dept:
            teachers = Teacher.objects.filter(department=dept)
            courses = Course.objects.filter(created_by__in=teachers)
            exams = Exam.objects.filter(course__in=courses)
            results = Result.objects.filter(exam__in=exams)
            
            avg_score = results.aggregate(Avg('score'))['score__avg'] or 0
            total_results = results.count()
            passed_results = results.filter(is_pass=True).count()
            pass_percentage = (passed_results / total_results * 100) if total_results > 0 else 0
            
            dept_data.append([dept, f"{avg_score:.2f}", f"{pass_percentage:.2f}%"])

    t_dept = Table(dept_data)
    t_dept.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t_dept)
    elements.append(Spacer(1, 20))

    # 3. AI Usage
    elements.append(Paragraph("AI System Usage", styles['Heading2']))
    ai_exams = Exam.objects.filter(creation_method='AI').count()
    manual_exams = Exam.objects.filter(creation_method='Manual').count()
    
    ai_data = [
        ['Method', 'Exams Created'],
        ['AI Generated', str(ai_exams)],
        ['Manual Creation', str(manual_exams)]
    ]
    t_ai = Table(ai_data)
    t_ai.setStyle(TableStyle([
         ('BACKGROUND', (0, 0), (-1, 0), colors.green),
         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
         ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t_ai)

    doc.build(elements)
    return response

# --- Student Dashboard Views ---

def student_dashboard(request):
    if request.session.get("role") != "student":
        return redirect("login")

    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login")

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect("login")
    
    courses = Course.objects.none()
    if student.department:
        # Using icontains to handle cases like 'cs' vs 'CSE' vs 'Computer Science' more gracefully
        courses = Course.objects.filter(department__icontains=student.department)
    
    # Taken Exams IDs
    taken_exam_ids = Result.objects.filter(student=student).values_list('exam_id', flat=True)

    # Upcoming Exams (Excluding taken ones)
    upcoming_exams = Exam.objects.filter(course__in=courses, status='Scheduled').exclude(id__in=taken_exam_ids).order_by('date')
    
    # Completed Exams (All history)
    completed_exams = Result.objects.filter(student=student).order_by('-created_at')

    # Completed Exams Count
    completed_exams_count = completed_exams.count()
    
    # Study Materials
    materials = StudyMaterial.objects.filter(course__in=courses, status='Approved').order_by('-uploaded_at')

    return render(request, "student_dashboard.html", {
        "student": student,
        "courses": courses,
        "upcoming_exams": upcoming_exams,
        "completed_exams": completed_exams,
        "completed_exams_count": completed_exams_count,
        "materials": materials,
    })

from django.http import JsonResponse
import json

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def submit_ai_query(request):
    if not request.session.get('role') == 'student':
         return JsonResponse({'error': 'Unauthorized'}, status=403)
         
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            course_id = data.get('course_id')

            student_id = request.session.get("student_id")
            if not student_id:
                 return JsonResponse({'error': 'Unauthorized'}, status=401)
            
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                 return JsonResponse({'error': 'Student not found'}, status=404)

            if not query:
                return JsonResponse({'error': 'No query provided'}, status=400)
                
            # Retrieve context material
            context_text = ""
            course = None
            if course_id:
                try:
                    course = Course.objects.get(id=course_id)
                    # Naive context: aggregate titles of materials
                    materials = StudyMaterial.objects.filter(course=course, status='Approved')
                    context_text = " ".join([m.title for m in materials])
                except Course.DoesNotExist:
                    pass # Course not found, proceed without course-specific context

            # Use SupportService
            support_bot = SupportService.get_instance()
            result = support_bot.get_clarification(query, context_text)
            
            ai_response = result['answer']
            
            # Log the query
            student = request.user
            
            if course:
                 AIClarificationLog.objects.create(
                    course=course,
                    student=student,
                    query_text=query
                )
            
            return JsonResponse({'response': ai_response, 'citation': result.get('relevant_section')})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)

def exam_interface(request, exam_id):
    if request.session.get("role") != "student":
        return redirect("login")

    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login")

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect("login")

    exam = Exam.objects.get(id=exam_id)
    questions = Question.objects.filter(exam=exam)

    return render(request, "exam_interface.html", {
        "exam": exam,
        "questions": questions,
        "student": student
    })

def submit_exam(request, exam_id):
    if request.method != "POST":
        return redirect("student_dashboard")

    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login")

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect("login")

    exam = Exam.objects.get(id=exam_id)

    if Result.objects.filter(exam=exam, student=student).exists():
        messages.warning(request, "Already submitted")
        return redirect("student_dashboard")

    result = Result.objects.create(
        exam=exam,
        student=student,
        score=0,
        is_pass=False,
        status="Pending"
    )

    grader = GradingService.get_instance()
    total_score = 0

    for q in Question.objects.filter(exam=exam):
        ans = request.POST.get(f"question_{q.id}", "")
        grade = grader.grade_submission(q.question_text, ans, q.answer)

        StudentAnswer.objects.create(
            result=result,
            question=q,
            student_answer=ans,
            ai_score=grade["score"],
            feedback=grade["feedback"]
        )

        total_score += grade["score"]

    result.score = total_score
    result.is_pass = total_score >= (len(Question.objects.filter(exam=exam)) * 0.4)
    result.status = "Completed"
    result.save()

    return redirect("student_dashboard")


# ===================================================
# PROCTORING ENDPOINT (IMPORTANT)
# ===================================================

@csrf_exempt
def proctoring_stream(request):
    """
    Receives webcam frames and returns calibration / proctoring status.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    try:
        # Lazy load to avoid OOM on import
        proctoring_engine = ProctoringService.get_instance()
        
        payload = json.loads(request.body)
        frame_data = payload.get("image")

        if not frame_data:
            return JsonResponse({"status": "error", "message": "No image data"})

        # Get calibration state from session or initialize default
        calibration_state = request.session.get('proctoring_calibration_state', None)
        # print(f"DEBUG: Calibration State: {calibration_state}")

        result, new_state = proctoring_engine.process_frame(frame_data, calibration_state)
        
        # Save updated state to session
        request.session['proctoring_calibration_state'] = new_state

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


# --- Admin Dashboard Views ---

def admin_dashboard(request):
    try:
        # Ensure user is a superuser/admin
        if not request.user.is_superuser:
            messages.error(request, "Access denied. Admin only.")
            return redirect('login')

        print("DEBUG: Admin Dashboard - User authorized")

        # 1. User Overview
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_hods = HOD.objects.count()
        total_principals = Principal.objects.count()
        
        # 2. Key System Metrics
        total_courses = Course.objects.count()
        total_exams = Exam.objects.count()
        
        # 3. Recent Registrations (Combined)
        recent_students = Student.objects.order_by('-created_at')[:5]
        
        # 4. Pending Approvals (Teachers)
        pending_teachers_count = Teacher.objects.filter(status=False).count()

        print("DEBUG: Admin Context Prepared")

        context = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_hods': total_hods,
            'total_principals': total_principals,
            'total_courses': total_courses,
            'total_exams': total_exams,
            'recent_students': recent_students,
            'pending_teachers_count': pending_teachers_count,
        }

        return render(request, 'admin_dashboard.html', context)
    except Exception as e:
        print(f"ERROR in admin_dashboard: {e}")
        return HttpResponse(f"Error loading dashboard: {e}")

def admin_user_list(request, role):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin only.")
        return redirect('login')

    users = []
    role_name = ""
    role = role.strip().lower()

    if role == 'student':
        users = Student.objects.all().order_by('-created_at')
        role_name = "Students"
    elif role == 'teacher':
        users = Teacher.objects.all().order_by('-created_at')
        role_name = "Teachers"
    elif role == 'hod':
        users = HOD.objects.all().order_by('-created_at')
        role_name = "HODs"
    elif role == 'principal':
        users = Principal.objects.all().order_by('-created_at')
        role_name = "Principals"
    else:
        messages.error(request, f"Invalid user role: {role}")
        return redirect('admin_dashboard')

    context = {
        'users': users,
        'role_key': role,
        'role_name': role_name
    }
    return render(request, 'admin_user_list.html', context)


def get_model_by_role(role):
    if role == 'student':
        return Student, 'student'
    elif role == 'teacher':
        return Teacher, 'teacher'
    elif role == 'hod':
        return HOD, 'hod'
    elif role == 'principal':
        return Principal, 'principal'
    return None, None

def edit_user(request, role, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    role = role.strip().lower()
    Model, _ = get_model_by_role(role)
    if not Model:
        messages.error(request, "Invalid role.")
        return redirect('admin_dashboard')
        
    try:
        user_obj = Model.objects.get(id=user_id)
    except Model.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('admin_user_list', role=role)

    if request.method == 'POST':
        # Common fields
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.email = request.POST.get('email')
        
        # Specific fields
        if role == 'teacher' or role == 'hod':
             user_obj.department = request.POST.get('department')
             
        user_obj.save()
        messages.success(request, f"{role.capitalize()} details updated successfully.")
        return redirect('admin_user_list', role=role)
        
    return render(request, 'admin_edit_user.html', {'user': user_obj, 'role': role})

def delete_user(request, role, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    role = role.strip().lower()
    Model, _ = get_model_by_role(role)
    if not Model:
        messages.error(request, "Invalid role.")
        return redirect('admin_dashboard')
        
    try:
        user_obj = Model.objects.get(id=user_id)
        user_obj.delete()
        messages.success(request, f"{role.capitalize()} deleted successfully.")
    except Model.DoesNotExist:
        messages.error(request, "User not found.")
        
    return redirect('admin_user_list', role=role)

def system_health(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    import psutil
    from django.db import connection
    
    # System Metrics
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    ram_total = round(psutil.virtual_memory().total / (1024**3), 2)
    ram_available = round(psutil.virtual_memory().available / (1024**3), 2)
    disk_usage = psutil.disk_usage('/').percent
    disk_total = round(psutil.disk_usage('/').total / (1024**3), 2)
    disk_free = round(psutil.disk_usage('/').free / (1024**3), 2)
    
    # DB Status
    db_status = "Unknown"
    try:
        connection.ensure_connection()
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {e}"
        
    context = {
        'cpu_usage': cpu_usage,
        'ram_usage': ram_usage,
        'ram_total': ram_total,
        'ram_available': ram_available,
        'disk_usage': disk_usage,
        'disk_total': disk_total,
        'disk_free': disk_free,
        'db_status': db_status
    }
    return render(request, 'admin_system_health.html', context)


# --- Department Management Views ---

def admin_department_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    departments = Department.objects.all().order_by('name')
    return render(request, 'admin_department_list.html', {'departments': departments})

def admin_add_department(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if Department.objects.filter(name=name).exists():
            messages.error(request, "Department already exists.")
            return render(request, 'admin_add_department.html', {'name': name, 'description': description})
            
        Department.objects.create(name=name, description=description)
        return redirect('admin_department_list')
        
    return render(request, 'admin_add_department.html', {'name': '', 'description': ''})

def admin_course_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'admin_course_list.html', {'courses': courses})

def admin_exam_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    exams = Exam.objects.all().order_by('-created_at')
    return render(request, 'admin_exam_list.html', {'exams': exams})

def admin_edit_department(request, dept_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    try:
        department = Department.objects.get(id=dept_id)
    except Department.DoesNotExist:
        messages.error(request, "Department not found.")
        return redirect('admin_department_list')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if Department.objects.filter(name=name).exclude(id=dept_id).exists():
            messages.error(request, "Department with this name already exists.")
            return render(request, 'admin_add_department.html', {'department': department, 'name': name, 'description': description})
            
        department.name = name
        department.description = description
        department.save()
        messages.success(request, "Department updated successfully.")
        return redirect('admin_department_list')
        
    return render(request, 'admin_add_department.html', {'department': department})

def admin_delete_department(request, dept_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('login')
        
    try:
        department = Department.objects.get(id=dept_id)
        department.delete()
        messages.success(request, "Department deleted successfully.")
    except Department.DoesNotExist:
        messages.error(request, "Department not found.")
        
    return redirect('admin_department_list')
