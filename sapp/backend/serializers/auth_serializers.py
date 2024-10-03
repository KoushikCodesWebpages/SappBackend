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

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
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
