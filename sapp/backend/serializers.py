from django.contrib.auth.models import User
from rest_framework import serializers
from .models import StudentsProfile, FacultyProfile

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        # Create a new user using the validated data
        user = User.objects.create_user(
            username=validated_data['email'],  # Set email as the username
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

class StudentsProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested UserSerializer to display user data

    class Meta:
        model = StudentsProfile
        fields = ['id', 'user', 'title', 'description', 'image', 'created_at', 'updated_at']

# Serializer for FacultyProfile
class FacultyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested UserSerializer to display user data

    class Meta:
        model = FacultyProfile
        fields = ['id', 'user', 'title', 'description', 'name', 'address', 'reg_no', 'website', 'created_at', 'updated_at']
