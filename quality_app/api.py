from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count, Q
from .models import Course, Exam, Result, StudyMaterial, ProctoringLog, AIClarificationLog, Teacher, User
import json

# --- Oversight Dashboard API ---

@require_http_methods(["GET"])
def get_oversight_analytics(request):
    """
    Returns analytics for the dashboard:
    1. Pass/Fail rates across all courses.
    2. Subject-wise average scores.
    3. AI Clarification usage per subject.
    """
    # 1. Pass/Fail Rates
    total_results = Result.objects.count()
    if total_results > 0:
        pass_count = Result.objects.filter(is_pass=True).count()
        pass_rate = (pass_count / total_results) * 100
        fail_rate = 100 - pass_rate
    else:
        pass_rate = 0
        fail_rate = 0

    # 2. Subject Performance (Avg Score)
    courses = Course.objects.annotate(avg_score=Avg('exam__result__score')).values('name', 'avg_score')
    
    # 3. AI Clarification Usage (Most queried subjects)
    ai_usage = AIClarificationLog.objects.values('course__name').annotate(query_count=Count('id')).order_by('-query_count')[:5]

    data = {
        "pass_fail_rate": {"pass": pass_rate, "fail": fail_rate},
        "subject_performance": list(courses),
        "ai_clarification_top_subjects": list(ai_usage)
    }
    return JsonResponse(data)


# --- Faculty Management API ---

@require_http_methods(["GET"])
def get_faculty_management_data(request):
    """
    Returns data for faculty management:
    1. List of teachers pending approval (or all teachers for role management).
    2. List of study materials pending review.
    """
    # Simply listing all teachers for now, assuming status field implies active/inactive or role needed
    teachers = Teacher.objects.values('id', 'first_name', 'last_name', 'department', 'status')
    
    pending_materials = StudyMaterial.objects.filter(status='Pending').values(
        'id', 'title', 'course__name', 'teacher__first_name', 'teacher__last_name', 'uploaded_at', 'file'
    )

    data = {
        "teachers": list(teachers),
        "pending_materials": list(pending_materials)
    }
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["POST"])
def manage_faculty_role(request):
    """
    Approve or modify teacher roles.
    Expects JSON: { "teacher_id": 1, "action": "approve" | "deactivate" }
    """
    try:
        body = json.loads(request.body)
        teacher_id = body.get('teacher_id')
        action = body.get('action')
        
        teacher = Teacher.objects.get(id=teacher_id)
        if action == 'approve':
            teacher.status = True # Assuming status=True means active/approved
        elif action == 'deactivate':
            teacher.status = False
        teacher.save()
        
        return JsonResponse({"status": "success", "message": f"Teacher {action}d successfully."})
    except Teacher.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Teacher not found."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def review_study_material(request):
    """
    Approve or reject study materials.
    Expects JSON: { "material_id": 1, "action": "approve" | "reject" }
    """
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
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# --- Exam Integrity API ---

@require_http_methods(["GET"])
def get_exam_integrity_report(request):
    """
    Returns consolidated anti-cheating flags.
    """
    # Count flags by type across all exams
    flag_counts = ProctoringLog.objects.values('flag_type').annotate(count=Count('id'))
    
    # Recent severe flags
    recent_flags = ProctoringLog.objects.filter(severity='High').values(
        'student__first_name', 'student__last_name', 'exam__title', 'flag_type', 'timestamp'
    ).order_by('-timestamp')[:10]

    data = {
        "flag_distribution": list(flag_counts),
        "recent_severe_incidents": list(recent_flags)
    }
    return JsonResponse(data)
