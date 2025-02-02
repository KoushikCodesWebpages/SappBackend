from rest_framework import serializers

from accounts.models import Student
from features.models import Announcement,Timetable,Attendance, AttendanceLock,CalendarEvent, Result, ResultLock, Assignment, Submission, Portion

class AttendanceLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLock
        fields = ['id', 'date', 'is_locked']
        
class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source='student.student_code')  # Display student_code in the response

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'date', 'status']

    def create(self, validated_data):
        # Extract the student_code from the validated data
        student_code = validated_data.get('student', None)

        if student_code:
            # Look up the Student object based on student_code
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                raise serializers.ValidationError({"student": "Student with the provided student_code does not exist."})
            validated_data['student'] = student  # Set the student field to the actual Student object

        # Create the Attendance object with the student relation
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Extract the student_code from the validated data
        student_code = validated_data.get('student', None)

        if student_code:
            # Look up the Student object based on student_code
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                raise serializers.ValidationError({"student": "Student with the provided student_code does not exist."})
            validated_data['student'] = student  # Set the student field to the actual Student object

        # Update the Attendance object with the new values
        return super().update(instance, validated_data)


class AnnouncementMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'date', 'timings']
        
class AnnouncementDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'description',
            'date',
            'timings',
            'offline_or_online',
            'till',
            'created_by',
            'created_at',
            'updated_at'
        ]

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'

class ResultLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultLock
        fields = ['id', 'title', 'start_date', 'end_date']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'student', 'subject', 'marks', 'total_marks', 'grade', 'result_lock']
        

    def validate(self, data):
        """
        Validate that:
        1. The result is being added during the active result lock period.
        2. Marks do not exceed total marks.
        3. Grade is calculated based on marks and total marks.
        """
        result_lock = data.get('result_lock')
        marks = data.get('marks')
        total_marks = data.get('total_marks')
        grade = data.get('grade')

        # Validate result lock period
        if result_lock and not result_lock.is_active():
            raise serializers.ValidationError("Results can only be added during the active result lock period. IN case the marks have to be changed, contact School Office.")

        # Validate marks and total marks
        if marks and total_marks:
            if marks > total_marks:
                raise serializers.ValidationError("Marks cannot exceed total marks. Kindly Put appropriate marks!")
            
            
            
class AssignmentMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title','subject','completed','due_date']
        
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        
class SubmissionMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'assignment_title', 'student', 'mark']
        
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        
class PortionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portion
        fields = '__all__'