from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from django.contrib.auth.models import User

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

from rest_framework import serializers
from django.contrib.auth import get_user_model
from backend.models.user_models import StudentsDB, FacultyDB, Section, Standard

User = get_user_model()
class SignUpSerializer(serializers.ModelSerializer):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty')
    ]
    role = serializers.ChoiceField(choices=ROLE_CHOICES)  # Adding a role field
    password = serializers.CharField(write_only=True)

    # Adding fields for standard and section
    standard = serializers.PrimaryKeyRelatedField(queryset=Standard.objects.all(), required=False)  # Assuming Standard is a model
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all(), required=False)  # Assuming Section is a model

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'standard', 'section']  # Adding role to the fields

    def create(self, validated_data):
        # Extract role from validated data
        role = validated_data.pop('role')
        standard = validated_data.pop('standard', None)  # Handle standard
        section = validated_data.pop('section', None)    # Handle section

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Create an entry in StudentsDB or FacultyDB based on the role
        if role == 'student':
            student_profile = StudentsDB.objects.create(user=user, standard=standard, section=section)  # Pass the standard and section
        elif role == 'faculty':
            faculty_profile = FacultyDB.objects.create(user=user)  # Add additional fields if necessary

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
