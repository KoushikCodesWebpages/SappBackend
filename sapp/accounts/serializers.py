from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, Faculty, OfficeAdmin
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
    class Meta:
        model = Student
        fields = ['user', 'enrollment_number', 'standard', 'section', 'subjects', 'attendance_percent']

# Faculty Serializer
class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['user', 'faculty_id', 'department', 'specialization', 'coverage', 'class_teacher']
        
class OfficeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeAdmin
        fields = ['user','employee_id','school_name']
        
class ExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()



class StudentNavbarSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Student
        fields = ['name']
        
class StudentProfileSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()  # Assuming this is your custom user serializer

    class Meta:
        model = Student
        fields = ['user', 'enrollment_number', 'standard', 'section', 'subjects', 'attendance_percent']

    def update(self, instance, validated_data):
        # Handle user update (username, email)
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update the student profile data
        return super().update(instance, validated_data)

class FacultyNavbarSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Faculty
        fields = ['name']
           
class FacultyProfileSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()

    class Meta:
        model = Faculty
        fields = ['user', 'faculty_id', 'department', 'specialization', 'coverage', 'class_teacher']
    
    def update(self, instance, validated_data):
        # Handle user update (username, email)
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update the student profile data
        return super().update(instance, validated_data)
    
    
