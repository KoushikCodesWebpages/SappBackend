from rest_framework import serializers


from accounts.serializers import UserSerializer 
from students.serializers import StudentsDBSerializer
from faculties.serializers import FacultyDBSerializer
from exposed.serializers import StandardSerializer, SectionSerializer

class ProfileSerializer(serializers.Serializer):
    user = UserSerializer()
    image = serializers.ImageField(required=False)
    standard = StandardSerializer(required=False)
    section = SectionSerializer(required=False)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False)
    student_profile = StudentsDBSerializer(required=False)  # Optional field for student profile
    faculty_profile = FacultyDBSerializer(required=False) 

    def validate(self, attrs):
        # Add any custom validation if needed
        return attrs
