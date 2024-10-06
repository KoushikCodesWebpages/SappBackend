from django.db import models
from django.contrib.auth.models import User
from backend.models.base_models import ProfileBase, Standard, Section, Subject
class StudentsDB(ProfileBase):
    """A model for storing student-specific profile information."""
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='students')  # Foreign key to Standard
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')    # Foreign key to Section

    def __str__(self):
        return f"Student Profile: {self.user.username}"


# Updated FacultyDB model
class FacultyDB(ProfileBase):
    """A model for storing faculty-specific profile information."""

    # Roles choices
    ROLE_CHOICES = [
        ('Teacher', 'Teacher'),
        ('Principal', 'Principal'),
        ('Coordinator', 'Coordinator'),
        ('Admin', 'Admin'),
        # Add more roles as needed
    ]
    
    name = models.CharField(max_length=255)  # Faculty name
    address = models.TextField()  # Faculty address
    reg_no = models.CharField(max_length=100, unique=True)  # Faculty registration number (assuming unique)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)  # Faculty role with choices
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='faculty', null=True, blank=True)  # Faculty assigned to section
    subjects = models.ManyToManyField(Subject, related_name='faculty')  # Faculty can teach multiple subjects

    def __str__(self):
        return f"Faculty Profile: {self.name}"