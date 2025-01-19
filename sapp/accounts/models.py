from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class AuthUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('office_admin', 'Office Admin')
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=False, null=False)
    is_verified = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.username} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_number = models.CharField(max_length=50, unique=True)
    standard= models.PositiveIntegerField()
    section = models.CharField(max_length=10, blank=True, null=True)
    subjects = models.JSONField(default=list)
    attendance_percent = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"Student: {self.user.username}"


class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=50, blank=True,null=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    subjects = models.JSONField(default=list)
    class_teacher = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Faculty: {self.user.username}"

    def set_class_teacher(self, standard, year):
        """
        Set the class teacher information.
        """
        self.class_teacher = {"standard": standard, "year": year}
        self.save()

    def get_class_teacher(self):
        """
        Get the class teacher information as a dictionary.
        """
        return self.class_teacher
    
class OfficeAdmin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='office_admin_profile')
    employee_id = models.CharField(max_length=50,blank=True, null=True)
    school_name = models.CharField(max_length=100)

