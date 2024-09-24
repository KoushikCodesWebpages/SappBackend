from django.db import models
from django.contrib.auth.models import User


class BaseDBModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class ProfileBase(BaseDBModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    class Meta:
        abstract = True


class Standard(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


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
    
    
