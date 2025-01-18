from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Student, Faculty

from rest_framework import serializers

from django.contrib.auth.models import User


class StudentSignupSerializer(serializers.ModelSerializer):
    # User-related fields
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    # Student-related fields
    roll_number = serializers.CharField(max_length=20, required=True)
    year_of_study = serializers.IntegerField(required=True)
    section = serializers.CharField(max_length=10, required=False, allow_blank=True)
    standard = serializers.CharField(max_length=50, required=True)
    subjects = serializers.ListField(child=serializers.CharField(), required=True)

    def create(self, validated_data):
        # Create the user first
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'password': validated_data['password']
        }
        user = User.objects.create_user(**user_data)
        
        # Create the student profile
        student_data = validated_data
        student_data.pop('username')
        student_data.pop('email')
        student_data.pop('password')
        student = Student.objects.create(user=user, **student_data)

        return student

    class Meta:
        model = Student
        fields = ['username', 'email', 'password', 'roll_number', 'year_of_study', 'section', 'standard', 'subjects']


class FacultySignupSerializer(serializers.ModelSerializer):
    # User-related fields
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    # Faculty-related fields
    employee_id = serializers.CharField(max_length=20, required=True)
    department = serializers.CharField(max_length=100, required=True)
    specialization = serializers.CharField(max_length=100, required=False, allow_blank=True)
    roles = serializers.ChoiceField(choices=Faculty.ROLES, default='lecturer')

    def create(self, validated_data):
        # Create the user first
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'password': validated_data['password']
        }
        user = User.objects.create_user(**user_data)
        
        # Create the faculty profile
        faculty_data = validated_data
        faculty_data.pop('username')  # Remove user-related fields
        faculty_data.pop('email')
        faculty_data.pop('password')
        
        # Create Faculty object
        faculty = Faculty.objects.create(user=user, **faculty_data)

        return faculty

    class Meta:
        model = Faculty
        fields = ['username', 'email', 'password', 'employee_id', 'department', 'specialization', 'roles']


class StudentLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
class FacultyLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
