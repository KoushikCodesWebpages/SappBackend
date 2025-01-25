from rest_framework import serializers

from .models import Attendance, AttendanceLock,CalendarEvent

from accounts.models import Student
from features.models import Announcement,Timetable

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




'''
class ProfileSerializer(serializers.Serializer):
    user = UserSerializer()
    image = serializers.ImageField(required=False)
    standard = StandardSerializer(required=False)
    section = SectionSerializer(required=False)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False)
    student_profile = StudentsDBSerializer(required=False)  # Optional field for student profile
    faculty_profile = FacultyDBSerializer(required=False) 

    def validate(self, attrs):
        # Add any custom validation if needed
        return attrs



class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = '__all__'
'''