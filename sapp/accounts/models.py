from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    roll_number = models.CharField(max_length=20, unique=True)
    year_of_study = models.PositiveIntegerField()
    section = models.CharField(max_length=10, blank=True, null=True)  # e.g., Section A, B, etc.
    standard = models.CharField(max_length=50)  # e.g., Grade 10, 12, etc.
    subjects = models.JSONField(default=list)  # List of subjects as JSON

    def __str__(self):
        return f"Student: {self.user.username} ({self.roll_number})"

class Faculty(models.Model):
    ROLES = [
        ('president', 'President'),
        ('vice president', 'Vice President'),
        ('class teacher', 'Class Teacher'),
        ('sub-teacher', 'Sub-Teacher'),
        ('lecturer', 'Lecturer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile")
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    roles = models.CharField(
        max_length=50,
        choices=ROLES,  # Use the ROLES list defined above
        default='lecturer',
    )
    
    def __str__(self):
        return f"Faculty: {self.user.username} ({self.employee_id})"

