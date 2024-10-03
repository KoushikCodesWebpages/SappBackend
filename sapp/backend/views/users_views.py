from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from serializers.user_serializers import StudentsDBSerializer, FacultyDBSerializer
from models.user_models import StudentsDB, FacultyDB
from utils.pagination import CustomPagination
from utils.utils import BaseDBView
from django.shortcuts import get_object_or_404


class StudentsProfileView(BaseDBView):
    model_class = StudentsDB
    serializer_class = StudentsDBSerializer
    permission_classes = [AllowAny]  # Only authenticated users can access this view
    pagination_class = CustomPagination


class FacultyProfileView(BaseDBView):
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

from rest_framework.generics import ListAPIView
from models.user_models import Standard,  Section
from rest_framework import serializers

class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = ['id', 'name']

class StandardListView(ListAPIView):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes = [AllowAny]
    
# Section Serializer
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']

# Section List View
class SectionListView(ListAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [AllowAny]
