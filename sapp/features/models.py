import uuid
from django.db import models
from django.utils.timezone import now

from accounts.models import Student
from django.core.exceptions import ValidationError

class Attendance(models.Model):
    student = models.ForeignKey(Student, related_name='attendance', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')])

    def __str__(self):
        return f"Attendance for {self.student.username} on {self.date}: {self.status}"
    
class AttendanceLock(models.Model):
    date = models.DateField()
    is_locked = models.BooleanField(default=False)

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
    created_by = models.CharField(max_length=255)  # Admin's username or email
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Methods
    @classmethod
    def get_latest_active(cls):
        """Fetch the latest active announcement."""
        return cls.objects.filter(till__gte=now()).order_by('-created_at').first()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

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
    created_by = models.CharField(max_length=255)  # Admin's username or email
    created_at = models.DateTimeField(auto_now_add=True)  # When the event was created
    updated_at = models.DateTimeField(auto_now=True)  # When the event was last updated

    def __str__(self):
        return f"{self.title} ({self.event_date})"

class Timetable(models.Model):
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standard = models.CharField(max_length=20)  # E.g., "7", "10"
    section = models.CharField(max_length=5)  # E.g., "A", "B"
    subject = models.CharField(max_length=100)  # Subject name (e.g., "Mathematics")
    faculty_name = models.CharField(max_length=255)  # Name of the assigned teacher/faculty
    day = models.CharField(
        max_length=10,
        choices=[
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
        ]
    )  # Day of the week
    start_time = models.TimeField()  # Start time of the class
    end_time = models.TimeField()  # End time of the class
    created_by = models.CharField(max_length=255)  # Admin's username or email
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update

    def __str__(self):
        return f"{self.standard}-{self.section} | {self.subject} | {self.day} ({self.start_time} - {self.end_time})"


class ResultLock(models.Model):
    title = models.CharField(max_length=100, unique=True)  # Unique title for the result lock
    start_date = models.DateField()  # Start date for result submission
    end_date = models.DateField()  # End date for result submission

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"

    def is_active(self):
        """Check if the result lock is currently active."""
        from django.utils import timezone
        return self.start_date <= timezone.now().date() <= self.end_date
    
    
class Result(models.Model):
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='results', 
        to_field='student_code')
    # Link to the Student model
    subject = models.CharField(max_length=100)  # Subject for which the result is recorded
    marks = models.PositiveIntegerField()  # Marks obtained by the student
    total_marks = models.PositiveIntegerField()
    grade = models.CharField(max_length=5)
    result_lock = models.ForeignKey(
        'ResultLock',
        on_delete=models.CASCADE,
        related_name='results',
        to_field='title'  # Use the 'title' field as the reference
    )  # Link to the ResultLock model

    def __str__(self):
        return f"{self.student.user.username} - {self.subject} ({self.marks})"

    def clean(self):
        """Validate that the result is being added within the active result lock period."""
        if not self.result_lock.is_active():
            raise ValidationError("Results can only be added during the active result lock period.")

    def save(self, *args, **kwargs):
        """Override the save method to enforce validation."""
        self.clean()  # Run validation before saving
        super().save(*args, **kwargs)
