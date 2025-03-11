from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class AuthUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('so_admin', 'SO Admin')
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=False, null=False)
    is_verified = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.username} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_number = models.CharField(max_length=50, unique=True)
    standard = models.PositiveIntegerField()
    section = models.CharField(max_length=10, blank=True, null=True)
    academic_year = models.CharField(max_length=20)
    subjects = models.JSONField(default=list)
    attendance_percent = models.PositiveIntegerField(default=0)
    student_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
      # New field for academic year
    image = models.ImageField(upload_to='students/pics/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Automatically generate the student_code before saving
        if not self.student_code:
            self.student_code = f"{self.user.email}-{self.standard}-{self.section}-{self.academic_year}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Student: {self.user.username} ({self.academic_year})"
    last_updated = models.DateTimeField(auto_now=True)


class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=50,unique=True)
    department = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    coverage = models.JSONField(default=list)  # Updated from 'subjects'
    class_teacher = models.JSONField(default=dict, blank=True)
    image = models.ImageField(upload_to='faculty/pics/', blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Faculty: {self.user.username}"

    def is_subject_teacher(self):
        """
        Check if the faculty is only a subject teacher.
        """
        return not bool(self.class_teacher)

    def add_coverage(self, standard, section, subject, academic_year):
        """
        Add a new subject coverage.
        """
        self.coverage.append([standard, section, subject, academic_year])
        self.save()

    def get_class_teacher(self):
        """
        Return the class teacher details.
        """
        return self.class_teacher
    
class SOAdmin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='office_admin_profile')
    employee_id = models.CharField(max_length=50,blank=True, null=True)
    school_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='office/pics/', blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    
