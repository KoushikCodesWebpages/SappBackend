from rest_framework import serializers

from .models import Assignment, Result, Report, Fee, Attendance, Timetable, CalendarEvent

from accounts.serializers import UserSerializer 
from students.serializers import StudentsDBSerializer
from faculties.serializers import FacultyDBSerializer
from exposed.serializers import StandardSerializer, SectionSerializer




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
