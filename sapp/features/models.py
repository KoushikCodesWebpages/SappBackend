'''from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)  # Mark if the notification is read
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.CharField(max_length=100)
    due_date = models.DateField()
    submitted_on = models.DateField(null=True, blank=True)
    class_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Assignment for {self.student.username}: {self.title}"

class Result(models.Model):
    student = models.ForeignKey(User, related_name='results', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    marks = models.FloatField()
    grade = models.CharField(max_length=10)

    def __str__(self):
        return f"Result for {self.student.username} in {self.subject}: {self.grade}"


class Report(models.Model):
    student = models.ForeignKey(User, related_name='reports', on_delete=models.CASCADE)
    report_title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"Report for {self.student.username}: {self.report_title}"


class Fee(models.Model):
    student = models.ForeignKey(User, related_name='fees', on_delete=models.CASCADE)
    amount_due = models.FloatField()
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Fees for {self.student.username}: {self.amount_due}"


class Attendance(models.Model):
    student = models.ForeignKey(User, related_name='attendance', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')])

    def __str__(self):
        return f"Attendance for {self.student.username} on {self.date}: {self.status}"


class Timetable(models.Model):
    class_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"Timetable for {self.class_name}: {self.subject} on {self.day_of_week}"


class CalendarEvent(models.Model):
    event_type = models.CharField(max_length=50, choices=[('exam', 'Exam'), ('fee_due', 'Fee Due')])
    description = models.TextField()
    event_date = models.DateField()

    def __str__(self):
        return f"{self.event_type} on {self.event_date}: {self.description}"

'''