from rest_framework import serializers
from django.contrib.auth.models import User
from ..models.models import StudentsDB, FacultyDB, Standard, Section

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


class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = ['id', 'name']


class StudentsDBSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = StudentsDB
        fields = ['id', 'user', 'image', 'standard', 'section', 'title', 'description']  # Add title and description

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class FacultyDBSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = FacultyDB
        fields = ['id', 'user', 'image', 'name', 'address', 'reg_no', 'role']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        faculty = FacultyDB.objects.create(user=user, **validated_data)
        return faculty
