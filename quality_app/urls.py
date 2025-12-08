from django.contrib import admin
from django.urls import path
from . import views, api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('principle-registration/', views.principle_registration, name='principle_registration'),
    path('hod-registration/', views.hod_registration, name='hod_registration'),
    path('hod-dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('teacher-registration/', views.teacher_registration, name='teacher_registration'),
    path('student-registration/', views.student_registration, name='student_registration'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('project/', views.project, name='project'),
    path('team/', views.team, name='team'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('404/', views.page_not_found, name='404'),
    
    # --- API Endpoints ---
    path('api/hod/oversight/', api.get_oversight_analytics, name='api_oversight'),
    path('api/hod/faculty-management/', api.get_faculty_management_data, name='api_faculty_mgmt'),
    path('api/hod/faculty-management/role/', api.manage_faculty_role, name='api_manage_role'),
    path('api/hod/faculty-management/material/', api.review_study_material, name='api_review_material'),
    path('api/hod/exam-integrity/', api.get_exam_integrity_report, name='api_exam_integrity'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)