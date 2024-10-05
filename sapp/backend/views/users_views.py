from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from backend.serializers.user_serializers import StudentsDBSerializer, FacultyDBSerializer, UserSerializer
from backend.models.user_models import StudentsDB, FacultyDB
from backend.utils.pagination import CustomPagination, SectionPagination, StandardPagination,SubjectPagination
from backend.utils.base_view import BaseDBView
from django.shortcuts import get_object_or_404


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
    

class ProfileAPI(APIView):
    permission_classes = [AllowAny]  # Ensure the user is logged in

    def get(self, request):
        # Get the logged-in user
        user = request.user

        # Fetch the student profile associated with the logged-in user
        student_profile = get_object_or_404(StudentsDB, user=user)

        # Serialize the student data
        serializer = StudentsDBSerializer(student_profile)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Get the logged-in user
        user = request.user

        # Check if the student profile already exists, otherwise create one
        student_profile, created = StudentsDB.objects.get_or_create(user=user)

        # Serialize the incoming data for validation and saving
        serializer = StudentsDBSerializer(student_profile, data=request.data, partial=True)

        # Check if the data is valid
        if serializer.is_valid():
            # Save the updated student profile
            serializer.save()

            # Return the updated or created student profile data
            return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        
        # If the data is not valid, return a 400 Bad Request with errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

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
