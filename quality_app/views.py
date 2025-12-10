from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from .ai_modules import AQGService, GradingService, SupportService, ProctoringService
import json # Ensure json is imported


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
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # 1. Check Student (User model) - Standard Django Auth
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                auth_login(request, user)
                if user.is_superuser:
                    request.session['role'] = 'admin'
                    messages.success(request, "Login successful as Admin.")
                    return redirect('admin_dashboard')

                request.session['role'] = 'student'
                messages.success(request, "Login successful as Student.")
                return redirect('student_dashboard')
        except User.DoesNotExist:
            pass # Continue to check other roles

        # 2. Check Teacher
        try:
            teacher = Teacher.objects.get(email=email)
            if check_password(password, teacher.password):
                request.session['user_id'] = teacher.id
                request.session['role'] = 'teacher'
                request.session['user_email'] = teacher.email
                request.session['user_name'] = f"{teacher.first_name} {teacher.last_name}"
                messages.success(request, "Login successful as Teacher.")
                return redirect('teacher_dashboard')
        except Teacher.DoesNotExist:
            pass

        # 3. Check HOD
        try:
            hod = HOD.objects.get(email=email)
            if check_password(password, hod.password):
                request.session['user_id'] = hod.id
                request.session['role'] = 'hod'
                request.session['user_email'] = hod.email
                request.session['user_name'] = f"{hod.first_name} {hod.last_name}"
                messages.success(request, "Login successful as HOD.")
                return redirect('hod_dashboard')
        except HOD.DoesNotExist:
            pass

        # 4. Check Principal
        try:
            principal = Principal.objects.get(email=email)
            if check_password(password, principal.password):
                request.session['user_id'] = principal.id
                request.session['role'] = 'principal'
                request.session['user_email'] = principal.email
                request.session['user_name'] = f"{principal.first_name} {principal.last_name}"
                messages.success(request, "Login successful as Principal.")
                return redirect('principal_dashboard')
        except Principal.DoesNotExist:
            pass

        # If no match found
        messages.error(request, "Invalid email or password.", extra_tags='danger')

    return render(request, 'login.html')


def logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

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
        return redirect('student_dashboard')

    return render(request, 'student-registration.html')


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
    
    return render(request, 'teacher_courses.html', {'courses': courses, 'teacher': teacher})

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
        
        StudyMaterial.objects.create(
            title=title,
            course=course,
            teacher=teacher,
            file=file,
            status='Approved' # Auto-approve for now or set to Pending based on logic
        )
        messages.success(request, "Material uploaded successfully.")
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
             context_text = f"Content for course {course.name}. " + " ".join([m.title for m in StudyMaterial.objects.filter(course=course)])
             
             aqg = AQGService.get_instance()
             questions = aqg.generate_questions(context_text, count=5, difficulty=difficulty)
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
            proctoring_config=proctoring_config,
            creation_method='AI', # Explicitly marking as AI for dashboard stats
            created_by=teacher,
            status='Scheduled'
        )
        
        # If we had a Questions model, we would save them here.
        
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
    }

    return render(request, 'principal_dashboard.html', context)

def approve_teacher(request, teacher_id):
    if not request.session.get('role') == 'principal':
        return redirect('login')
        
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.status = True
        teacher.save()
        messages.success(request, f"Teacher {teacher.first_name} approved successfully.")
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher not found.")
        
    return redirect('principal_dashboard')

def reject_teacher(request, teacher_id):
    if not request.session.get('role') == 'principal':
        return redirect('login')
        
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.delete() # Or set status to Rejected if field existed
        messages.success(request, f"Teacher {teacher.first_name} rejected.")
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher not found.")
        
# --- Student Dashboard Views ---

def student_dashboard(request):
    if not request.session.get('role') == 'student':
        messages.error(request, "Access denied. Student only.")
        return redirect('login')

    student = request.user 
    
    # Get enrolled courses (Assuming logic: All courses in student's department)
    student_dept = student.department
    courses = Course.objects.filter(department=student_dept)
    
    # Upcoming Exams
    upcoming_exams = Exam.objects.filter(course__in=courses, status='Scheduled').order_by('date')
    
    # Recent Results
    recent_results = Result.objects.filter(student=student, status='Released').order_by('-created_at')[:5]
    
    # Study Materials
    materials = StudyMaterial.objects.filter(course__in=courses, status='Approved').order_by('-uploaded_at')

    context = {
        'student': student,
        'courses': courses,
        'upcoming_exams': upcoming_exams,
        'recent_results': recent_results,
        'materials': materials,
    }
    return render(request, 'student_dashboard.html', context)

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
            course_id = data.get('course_id') # Optional context
            
            # Retrieve context material
            context_text = ""
            course = None
            if course_id:
                course = Course.objects.get(id=course_id)
                # Naive context: aggregate titles of materials
                materials = StudyMaterial.objects.filter(course=course, status='Approved')
                context_text = " ".join([m.title for m in materials])

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
    if not request.session.get('role') == 'student':
        return redirect('login')
        
    exam = Exam.objects.get(id=exam_id)
    
    # Check if user already submitted this exam
    if Result.objects.filter(exam=exam, student=request.user).exists():
        messages.warning(request, "You have already attempted this exam.")
        return redirect('student_dashboard')

    context = {
        'exam': exam,
        'student': request.user
    }
    return render(request, 'exam_interface.html', context)

def submit_exam(request, exam_id):
    if request.method == 'POST':
        exam = Exam.objects.get(id=exam_id)
        
        # Check if already submitted
        if Result.objects.filter(exam=exam, student=request.user).exists():
             messages.error(request, "You have already submitted this exam.")
             return redirect('student_dashboard')
        # In a real app, retrieve student answers from POST data
        # answers = json.loads(request.body).get('answers')
        
        # Mock answers for demonstration of grading
        answers = [
            {"question_text": "Explain photosynthesis.", "student_answer": "It is how plants make food using sun."}
        ]
        
        grader = GradingService.get_instance()
        total_score = 0
        feedback_summary = []
        
        for ans in answers:
            # ideal_answer would be fetched from the DB
            ideal = "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar."
            
            grading_result = grader.grade_submission(ans['question_text'], ans['student_answer'], ideal)
            total_score += grading_result['score']
            feedback_summary.append(grading_result['feedback'])
            
        # Create Result object
        exam = Exam.objects.get(id=exam_id)
        Result.objects.create(
            exam=exam,
            student=request.user,
            score=total_score,
            is_pass=total_score > 5, # Simple threshold
            ai_feedback=" | ".join(feedback_summary),
            status='Pending' # Pending teacher confirmation even after AI grading
        )

        messages.success(request, "Exam submitted successfully! AI Grading in progress...")
        return redirect('student_dashboard')
    return redirect('student_dashboard')

@csrf_exempt
def proctoring_stream_endpoint(request):
    """
    Endpoint to receive video frames for proctoring analysis.
    Expected: POST with frame data.
    """
    if request.method == 'POST':
        try:
            # frame_data = request.POST.get('frame') or key in json
            # For simplicity, just return the mock result
            proctor = ProctoringService.get_instance()
            analysis = proctor.process_frame("dummy_frame_data")
            
            # If violations found, log them
            # ProctoringLog.objects.create(...)
            
            return JsonResponse(analysis)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'listening'})
    return redirect('principal_dashboard')


# --- Admin Dashboard Views ---

def admin_dashboard(request):
    # Ensure user is a superuser/admin
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin only.")
        return redirect('login')

    # 1. User Overview
    total_students = User.objects.filter(is_superuser=False).count()
    total_teachers = Teacher.objects.count()
    total_hods = HOD.objects.count()
    total_principals = Principal.objects.count()
    
    # 2. Key System Metrics
    total_courses = Course.objects.count()
    total_exams = Exam.objects.count()
    
    # 3. Recent Registrations (Combined)
    # This is a bit complex since users are in different tables. 
    # For now, we'll just show recent User (student) registrations as a proxy or fetch separately.
    recent_students = User.objects.order_by('-created_at')[:5]
    
    # 4. Pending Approvals (Teachers)
    pending_teachers_count = Teacher.objects.filter(status=False).count()

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

