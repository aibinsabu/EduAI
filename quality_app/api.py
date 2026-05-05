from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count, Q
from .models import Course, Exam, Result, StudyMaterial, ProctoringLog, AIClarificationLog, Teacher, User, Student, HOD, Principal
import json
import traceback

# --- Oversight Dashboard API ---

@require_http_methods(["GET"])
def get_oversight_analytics(request):
    try:
        # Get HOD's department if applicable
        dept = None
        if request.session.get('role') == 'hod':
            hod_id = request.session.get('user_id')
            hod = HOD.objects.get(id=hod_id)
            dept = hod.department

        # Base querysets
        results_qs = Result.objects.all()
        courses_qs = Course.objects.all()
        ai_logs_qs = AIClarificationLog.objects.all()

        if dept:
            results_qs = results_qs.filter(exam__course__department=dept)
            courses_qs = courses_qs.filter(department=dept)
            ai_logs_qs = ai_logs_qs.filter(course__department=dept)

        # 1. Pass/Fail Rates
        total_results = results_qs.count()
        if total_results > 0:
            pass_count = results_qs.filter(is_pass=True).count()
            pass_rate = (pass_count / total_results) * 100
            fail_rate = 100 - pass_rate
        else:
            pass_rate = 0
            fail_rate = 0

        # 2. Subject Performance (Avg Score)
        courses = courses_qs.annotate(avg_score=Avg('exam__result__score')).values('name', 'avg_score')
        
        # 3. AI Clarification Usage (Most queried subjects)
        ai_usage = ai_logs_qs.values('course__name').annotate(query_count=Count('id')).order_by('-query_count')[:5]

        data = {
            "pass_fail_rate": {"pass": pass_rate, "fail": fail_rate},
            "subject_performance": list(courses),
            "ai_clarification_top_subjects": list(ai_usage)
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"Error in get_oversight_analytics: {e}")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


# --- Faculty Management API ---

@require_http_methods(["GET"])
def get_faculty_management_data(request):
    try:
        dept = None
        if request.session.get('role') == 'hod':
            hod_id = request.session.get('user_id')
            hod = HOD.objects.get(id=hod_id)
            dept = hod.department

        teachers_qs = Teacher.objects.all()
        materials_qs = StudyMaterial.objects.filter(status='Pending')

        if dept:
            teachers_qs = teachers_qs.filter(department=dept)
            materials_qs = materials_qs.filter(course__department=dept)

        teachers = teachers_qs.values('id', 'first_name', 'last_name', 'department', 'status')
        pending_materials = materials_qs.values(
            'id', 'title', 'course__name', 'teacher__first_name', 'teacher__last_name', 'uploaded_at', 'file'
        )

        data = {
            "teachers": list(teachers),
            "pending_materials": list(pending_materials)
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"Error in get_faculty_management_data: {e}")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def manage_faculty_role(request):
    try:
        body = json.loads(request.body)
        teacher_id = body.get('teacher_id')
        action = body.get('action')
        
        teacher = Teacher.objects.get(id=teacher_id)
        if action == 'approve':
            teacher.status = True
        elif action == 'deactivate':
            teacher.status = False
        teacher.save()
        
        return JsonResponse({"status": "success", "message": f"Teacher {action}d successfully."})
    except Teacher.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Teacher not found."}, status=404)
    except Exception as e:
        print(f"Error in manage_faculty_role: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def review_study_material(request):
    try:
        body = json.loads(request.body)
        material_id = body.get('material_id')
        action = body.get('action')
        
        material = StudyMaterial.objects.get(id=material_id)
        if action == 'approve':
            material.status = 'Approved'
        elif action == 'reject':
            material.status = 'Rejected'
        material.save()
        
        return JsonResponse({"status": "success", "message": f"Material {action}d."})
    except StudyMaterial.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Material not found."}, status=404)
    except Exception as e:
        print(f"Error in review_study_material: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# --- Exam Integrity API ---

@require_http_methods(["GET"])
def get_exam_integrity_report(request):
    try:
        dept = None
        if request.session.get('role') == 'hod':
            hod_id = request.session.get('user_id')
            hod = HOD.objects.get(id=hod_id)
            dept = hod.department

        logs_qs = ProctoringLog.objects.all()

        if dept:
            logs_qs = logs_qs.filter(exam__course__department=dept)

        # 1. Count flags by type across all exams
        flag_counts = logs_qs.values('flag_type').annotate(count=Count('id'))

        # 2. Recent severe flags (all High severity) — latest 10
        recent_flags = logs_qs.filter(severity='High').values(
            'student__first_name', 'student__last_name',
            'student__department', 'student__registration_no',
            'exam__title', 'flag_type', 'timestamp', 'severity'
        ).order_by('-timestamp')[:10]

        # 3. Unusual submissions: fullscreen exits and forced submissions
        unusual_qs = logs_qs.filter(
            flag_type__icontains='Fullscreen Exit'
        ) | logs_qs.filter(
            flag_type__icontains='Forced Submission'
        )

        unusual_submissions = unusual_qs.values(
            'student__first_name', 'student__last_name',
            'student__department', 'student__registration_no',
            'exam__title', 'flag_type', 'timestamp', 'severity'
        ).order_by('-timestamp')[:20]

        # 4. Per-student fullscreen exit summary (aggregated)
        exit_summary = logs_qs.filter(
            flag_type__icontains='Fullscreen Exit'
        ).values(
            'student__first_name', 'student__last_name',
            'student__department', 'exam__title'
        ).annotate(exit_count=Count('id')).order_by('-exit_count')[:10]

        # 5. Forced submission count
        forced_count = logs_qs.filter(
            flag_type__icontains='Forced Submission'
        ).count()

        data = {
            "flag_distribution": list(flag_counts),
            "recent_severe_incidents": list(recent_flags),
            "unusual_submissions": list(unusual_submissions),
            "fullscreen_exit_summary": list(exit_summary),
            "forced_submission_count": forced_count,
            "department": dept or "All Departments"
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"Error in get_exam_integrity_report: {e}")
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_department_exams(request):
    try:
        dept = None
        if request.session.get('role') == 'hod':
            hod_id = request.session.get('user_id')
            hod = HOD.objects.get(id=hod_id)
            dept = hod.department
        elif request.session.get('role') == 'principal' or request.user.is_superuser:
            pass # Principal sees all
        else:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        exams_qs = Exam.objects.all()
        if dept:
            exams_qs = exams_qs.filter(course__department=dept)

        # Annotate with attendance count (Result count)
        exams = exams_qs.annotate(attendance_count=Count('result')).values(
            'id', 'title', 'course__name', 'start_time', 'end_time', 'attendance_count'
        ).order_by('-start_time')

        return JsonResponse({"exams": list(exams)})
    except Exception as e:
        print(f"Error in get_department_exams: {e}")
        return JsonResponse({"error": str(e)}, status=500)
