from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('home/', views.home, name="home"),
    path('', views.index, name="index"),
    path('index/', views.index, name="index_html"),
    path('about/', views.about, name="about"),
    path('service/', views.service, name="service"),
    path('project/', views.project, name="project"),
    path('team/', views.team, name="team"),
    path('testimonial/', views.testimonial, name="testimonial"),  # <-- Add this line
    path('404.html', views.page_not_found, name="404"),
    path('principle-registration/', views.principle_registration, name="principle_registration"),
    path('hod-registration/', views.hod_registration, name="hod_registration"),
    path('teacher-registration/', views.teacher_registration, name="teacher_registration"),
    path('student-registration/', views.student_registration, name="student_registration"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)