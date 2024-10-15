from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model

from accounts.models import Section, Standard
from students.models import StudentsDB
from faculties.models import FacultyDB

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty')
    ]
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    password = serializers.CharField(write_only=True)
    standard = serializers.PrimaryKeyRelatedField(queryset=Standard.objects.all(), required=False)
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'standard', 'section']

    def validate(self, attrs):
        role = attrs.get('role')
        standard = attrs.get('standard')
        section = attrs.get('section')

        if role == 'student' and (not standard or not section):
            raise serializers.ValidationError("Standard and section are required for students.")
        
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role')
        standard = validated_data.pop('standard', None)
        section = validated_data.pop('section', None)

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Handle profile creation
        if role == 'student':
            # Check if the student profile already exists
            if StudentsDB.objects.filter(user=user).exists():
                raise serializers.ValidationError("Student profile already exists.")
            StudentsDB.objects.create(user=user, standard=standard, section=section)
        
        elif role == 'faculty':
            # Check if the faculty profile already exists
            if FacultyDB.objects.filter(user=user).exists():
                raise serializers.ValidationError("Faculty profile already exists.")
            FacultyDB.objects.create(user=user)  # Include additional fields if needed
        
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid login credentials')

        if not user.check_password(password):
            raise AuthenticationFailed('Invalid login credentials')

        return {
            'username': user.username,  # You can return other user info if needed
        }
        
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email found.")
        return value
    
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],  # Set email as the username
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user



