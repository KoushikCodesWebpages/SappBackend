from django.db import models
from django.contrib.auth.models import User

class BaseDBModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    '''status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ])
    '''

    class Meta:
        abstract = True

# StudentsProfile inherits from BaseDBModel and adds a OneToOne relation to User
class StudentsProfile(BaseDBModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    # You can add more student-specific fields here

    def __str__(self):
        return self.user.username

# FacultyProfile inherits from BaseDBModel and adds a OneToOne relation to User
class FacultyProfile(BaseDBModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField()
    reg_no = models.CharField(max_length=100)
    website = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # You can add more faculty-specific fields here

    def __str__(self):
        return self.name
