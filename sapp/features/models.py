import uuid
from django.db import models
from django.utils.timezone import now

from accounts.models import Student, Faculty
from django.core.exceptions import ValidationError

class Attendance(models.Model):
    date = models.DateField()
    student = models.ForeignKey(Student, related_name='attendance', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date')
        
    def __str__(self):
        return f"Attendance for {self.student.username} on {self.date}: {self.status}"
    
    
class AttendanceLock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    is_locked = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('id', 'date')

    def __str__(self):
        return f"Attendance lock for {self.date}: {'Locked' if self.is_locked else 'Open'}"
    

    
class Announcement(models.Model):
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    timings = models.CharField(max_length=100)
    offline_or_online = models.CharField(max_length=50, choices=(('Offline', 'Offline'), ('Online', 'Online')))
    till = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True) 

    # Methods
    @classmethod
    def get_latest_active(cls):
        """Fetch the latest active announcement."""
        return cls.objects.filter(till__gte=now()).order_by('-created_at').first()

    def __str__(self):
        return self.title

class CalendarEvent(models.Model):
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)  # Event title
    description = models.TextField()  # Event description
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('exam', 'Exam'),
            ('fee_due', 'Fee Due')
        ]
    )  # Type of event
    event_date = models.DateField()  # Date of the event
    last_updated = models.DateTimeField(auto_now=True)  # When the event was last updated

    def __str__(self):
        return f"{self.title} ({self.event_date})"


class Timetable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.CharField(max_length=9)  # Example: "2024-2025"
    standard = models.CharField(max_length=20)  # E.g., "7", "10"
    section = models.CharField(max_length=5)  # E.g., "A", "B"
    faculty_name = models.CharField(max_length=255)  # Assigned teacher
    created_by = models.CharField(max_length=255)  # Admin's username or email  

    # Fields for each weekday containing lists of subjects/periods
    monday = models.JSONField(default=list)  
    tuesday = models.JSONField(default=list)
    wednesday = models.JSONField(default=list)
    thursday = models.JSONField(default=list)
    friday = models.JSONField(default=list)

    def __str__(self):
        return f"{self.academic_year} | {self.standard}-{self.section} | {self.faculty_name}"



    def __str__(self):
        return f"{self.standard}-{self.section} | {self.subject} | {self.day} ({self.start_time} - {self.end_time})"


class ResultLock(models.Model):
    title = models.CharField(max_length=100, unique=True, db_index=True)  # Indexed for faster lookups
    start_date = models.DateField(db_index=True)  # Indexed to speed up range queries
    end_date = models.DateField(db_index=True)  # Indexed for efficient filtering
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"

    @property
    def is_active(self):
        """Check if the result lock is currently active."""
        today = now().date()
        return self.start_date <= today <= self.end_date

    

class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'accounts.Student', 
        on_delete=models.CASCADE, 
        related_name='results',
        to_field='student_code',
        db_index=True
    )
    result_lock = models.ForeignKey(
        'ResultLock',
        on_delete=models.CASCADE,
        related_name='results',
        to_field='title',
        db_index=True
    )   # Link to the ResultLock model
    
    subject = models.CharField(max_length=100)  # Subject for which the result is recorded
    marks = models.JSONField()  # Marks obtained by the student
    # Auto-set to the editor
    last_updated = models.DateTimeField(auto_now=True)  

    class Meta:
        unique_together = ('student', 'result_lock')
        indexes = [
            models.Index(fields=['student', 'result_lock']),
            models.Index(fields=['last_updated']),
        ]
    
    def percentage(self):
        """Compute percentage dynamically from the JSON field."""
        return round((self.marks["obtained"] / self.marks["total"]) * 100, 2) if self.marks.get("total") else 0

    def __str__(self):
        return f"{self.student} - {self.result_lock.title} ({self.marks['obtained']}/{self.marks['total']})"

    def clean(self):
        """Validate that the result is being added within the active result lock period."""
        if not self.result_lock.is_active:
            raise ValidationError("Results can only be added during the active result lock period.")

    def save(self, *args, **kwargs):
        """Override save to set created_by dynamically."""
        user = kwargs.pop('user', None)  # Extract user if passed from the view
        if not self.pk and user:  # Only set on creation
            self.created_by = user.username
        super().save(*args, **kwargs)



class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for assignment
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    mark = models.IntegerField(null=True, blank=True)  # Mark/grade for the assignment
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='assignments', to_field='faculty_id')
    due_date = models.DateTimeField(null=True, blank=True)
    standard = models.CharField(max_length=100)
    section = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20)
    completed = models.BooleanField(default=False)  # Flag for completed assignment
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Model for Submissions
class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for submission
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')  # assuming Student model
    image = models.ImageField(upload_to='submissions/images/', null=True, blank=True)
    document = models.FileField(upload_to='submissions/docs/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    mark = models.IntegerField(null=True, blank=True)  # Individual mark for the submission
    feedback = models.TextField(null=True, blank=True)  # Feedback from the faculty
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Submission by {self.student} for {self.assignment.title}"

    def save(self, *args, **kwargs):
        # Check if all submissions are made, if so, mark the assignment as completed
        super().save(*args, **kwargs)
        if self.assignment.submissions.count() == self.assignment.faculty.students.count():
            self.assignment.completed = True
            self.assignment.save()
            
            
class Portion(models.Model):
    standard = models.CharField(max_length=50, help_text="Standard or grade level")
    subject = models.CharField(max_length=100, help_text="Subject name")
    academic_year = models.CharField(max_length=9, help_text="Academic year (e.g., 2024-2025)")
    
    unit = models.JSONField(help_text="List of unit names")
    title = models.JSONField(help_text="List of portion titles")
    description = models.TextField(blank=True, help_text="Detailed description of the portion")
    reference = models.CharField(max_length=255, help_text="Reference information")
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.standard} - {self.subject} - {', '.join(self.unit)} - {', '.join(self.title)}"