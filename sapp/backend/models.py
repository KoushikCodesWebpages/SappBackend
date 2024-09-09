# models.py
from django.db import models

class BaseDBModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ])

    class Meta:
        abstract = True

# Then, for each database, you can create a model that inherits from BaseDBModel
class Assignment(BaseDBModel):
    # Add fields for class and section
    due_date = models.DateField(null=True, blank=True)  # Assignment due date
    assigned_by = models.CharField(max_length=255)  # Teacher who assigned it
    class_name = models.CharField(max_length=50)  # Class (e.g., 10th, 12th, etc.)
    section = models.CharField(max_length=5)  # Section (e.g., A, B, C)
'''
class Report(BaseDBModel):
    # Add any additional fields specific to the Report database
    pass

# And so on...
'''