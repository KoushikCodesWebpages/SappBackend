from django.db import models
from accounts.models import ProfileBase, Standard, Section

class StudentsDB(ProfileBase):
    """A model for storing student-specific profile information."""
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='students')  # Foreign key to Standard
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')    # Foreign key to Section

    def __str__(self):
        return f"Student Profile: {self.user.username}"
