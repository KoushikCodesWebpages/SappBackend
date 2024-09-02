from django.contrib.auth.models import User
from rest_framework import serializers

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
