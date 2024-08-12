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
    # Add any additional fields specific to the Assignment database
    pass
'''
class Report(BaseDBModel):
    # Add any additional fields specific to the Report database
    pass

# And so on...
'''