from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from backend.serializers.user_serializers import StudentsDBSerializer, FacultyDBSerializer, UserSerializer , ProfileSerializer , StandardSerializer, SectionSerializer, SubjectSerializer
from backend.models.user_models import StudentsDB, FacultyDB
from backend.utils.pagination import CustomPagination, SectionPagination, StandardPagination,SubjectPagination
from backend.utils.base_view import BaseDBView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound


class StudentsDbView(BaseDBView):
    model_class = StudentsDB
    serializer_class = StudentsDBSerializer
    permission_classes = [AllowAny]  # Only authenticated users can access this view
    pagination_class = CustomPagination


class FacultyDbView(BaseDBView):
    model_class = FacultyDB
    serializer_class = FacultyDBSerializer
    permission_classes = [AllowAny]  # Only authenticated users can access this view
    pagination_class = CustomPagination
    

class ProfileSerializer(serializers.Serializer):
    user = UserSerializer()
    image = serializers.ImageField(required=False)
    standard = StandardSerializer(required=False)
    section = SectionSerializer(required=False)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False)

    def validate(self, attrs):
        # Add any custom validation if needed
        return attrs

class ProfileView(BaseDBView):
    serializer_class = ProfileSerializer  # Using ProfileSerializer for reading user profile
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile_data = {}

        # Fetch student profile
        try:
            student = StudentsDB.objects.get(user=user)
            profile_data['student_profile'] = StudentsDBSerializer(student).data
        except StudentsDB.DoesNotExist:
            profile_data['student_profile'] = None

        # Fetch faculty profile (not included in the response)
        try:
            faculty = FacultyDB.objects.get(user=user)  # Optional logic for faculty
        except FacultyDB.DoesNotExist:
            pass  # Do nothing if faculty doesn't exist

        return Response(profile_data)

    def patch(self, request):
        user = request.user
        profile_data = {}

        # Update student profile if it exists
        try:
            student = StudentsDB.objects.get(user=user)
            student_serializer = StudentsDBSerializer(student, data=request.data, partial=True)
            if student_serializer.is_valid(raise_exception=True):
                student_serializer.save()
                profile_data['student_profile'] = student_serializer.data
            else:
                return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentsDB.DoesNotExist:
            return Response({"error": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(profile_data)


    

# Exposed APIs

from backend.models.user_models import Standard,  Section, Subject
from backend.serializers.user_serializers import StandardSerializer, SectionSerializer,SubjectSerializer


class StandardView(BaseDBView):
    model_class = Standard
    serializer_class = StandardSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    
class SubjectView(BaseDBView):
    model_class = Subject
    serializer_class = SubjectSerializer
    pagination_class = SubjectPagination
    permission_classes = [AllowAny]

class SectionView(BaseDBView):
    model_class = Section
    serializer_class = SectionSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
