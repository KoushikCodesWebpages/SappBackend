# backend/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('email', ''),  # Use email as username or customize as needed
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user