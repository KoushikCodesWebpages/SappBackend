from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, Faculty, SOAdmin
from django.contrib.auth import get_user_model
import pandas as pd

# Custom User Serializer
class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'role']
        
    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise ValidationError("This username is already taken.")
        return value

# Student Serializer
class StudentSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()
    class Meta:
        model = Student
        fields = ['user', 'enrollment_number', 'standard', 'section','academic_year', 'subjects', 'attendance_percent','image','student_code','last_updated']

# Faculty Serializer
class FacultySerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()
    class Meta:
        model = Faculty
        fields = ['user', 'faculty_id', 'department', 'specialization', 'coverage', 'class_teacher','image','last_updated']
        
class OfficeAdminSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()
    class Meta:
        model = SOAdmin
        fields = ['user','employee_id','school_name','image','last_updated']
        
class ExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()



'''class StudentNavbarSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Student
        fields = ['name']
'''
        

