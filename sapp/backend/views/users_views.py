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
    serializer_class = ProfileSerializer  # Use ProfileSerializer

    def get_user_profile(self, user):
        """Fetch the user profile based on user type."""
        if hasattr(user, 'studentsdb'):
            return StudentsDB.objects.get(user=user), StudentsDB
        elif hasattr(user, 'facultydb'):
            return FacultyDB.objects.get(user=user), FacultyDB
        else:
            raise ValueError("User profile not found.")

    def get(self, request):
        try:
            profile, model_class = self.get_user_profile(request.user)
            serializer = self.serializer_class(profile)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        try:
            profile, model_class = self.get_user_profile(request.user)
            serializer = self.serializer_class(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile, model_class = self.get_user_profile(request.user)
            serializer = self.serializer_class(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


    

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
