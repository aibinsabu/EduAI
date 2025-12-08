from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# Custom user model
class User(AbstractUser):
    email = models.EmailField(unique=True)  
    phone = models.CharField(max_length=15, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile = models.ImageField(upload_to="profile/")
    date_of_birth = models.DateField(null=True, blank=True)
    registration_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    username = None

    objects = CustomUserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.fullname

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Principal(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10,)
    registration_no = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    password = models.CharField(max_length=100)
    profile = models.ImageField(upload_to="profile/principal/")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'principal'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Teacher(models.Model):
    

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, )
    registration_no = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100,)
    address = models.TextField()
    password = models.CharField(max_length=100)
    profile = models.ImageField(upload_to="profile/teacher/")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'teacher'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class HOD(models.Model):
    

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10,)
    registration_no = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100,)
    address = models.TextField()
    password = models.CharField(max_length=100)
    profile = models.ImageField(upload_to="profile/hod/")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'hod'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# --- HOD Interface Models ---

class Course(models.Model):
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Exam(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    status = models.CharField(max_length=20, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed')], default='Scheduled')
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE) # Assuming User can be a student
    score = models.FloatField()
    is_pass = models.BooleanField()
    ai_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    file = models.FileField(upload_to="study_materials/")
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ProctoringLog(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    flag_type = models.CharField(max_length=50) # e.g., 'Gaze', 'Screen', 'Audio'
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])

class AIClarificationLog(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
