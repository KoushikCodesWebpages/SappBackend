from django.db import models
from django.contrib.auth.models import User
from models.base_models import ProfileBase, Standard, Section

class StudentsDB(ProfileBase):
    """A model for storing student-specific profile information."""
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='students')  # Foreign key to Standard
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')    # Foreign key to Section

    def __str__(self):
        return f"Student Profile: {self.user.username}"


class FacultyDB(ProfileBase):
    """A model for storing faculty-specific profile information."""
    name = models.CharField(max_length=255)  # Faculty name field
    address = models.TextField()  # Faculty address
    reg_no = models.CharField(max_length=100, unique=True)  # Faculty registration number (assuming unique)
    role = models.CharField(max_length=255)  # Faculty role

    def __str__(self):
        return f"Faculty Profile: {self.name}"