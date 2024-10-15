from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import serializers
from students.models import StudentsDB
from accounts.serializers import UserSerializer, StandardSerializer, SectionSerializer


class StudentsDBSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    standard = StandardSerializer()  # Nested serializer for standard
    section = SectionSerializer()    # Nested serializer for section
    title = serializers.SerializerMethodField()  # Use SerializerMethodField to get the username

    class Meta:
        model = StudentsDB
        fields = ['id', 'user', 'image', 'standard', 'section', 'title', 'description']  # Ensure all relevant fields are included

    def get_title(self, obj):
        return obj.user.username  # Return the username as the title

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

    def create(self, validated_data):
        user_data = validated_data.pop('user')  # Pop user data from the validated data
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)

        # Create the student instance with the user instance
        student = StudentsDB.objects.create(user=user, **validated_data)
        
        # Set the title to the username and save
        student.title = user.username  
        student.save()  # Save the student instance to persist the title

        return student