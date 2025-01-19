from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Student, Faculty, OfficeAdmin
from django.contrib.auth import get_user_model
import pandas as pd

# Custom User Serializer
class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'role']

# Student Serializer
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['user', 'enrollment_number', 'standard', 'section', 'subjects', 'attendance_percent']

# Faculty Serializer
class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['user', 'faculty_id', 'department', 'specialization', 'subjects', 'class_teacher']
        
class OfficeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeAdmin
        fields = ['user','employee_id','school_name']
        
class ExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()