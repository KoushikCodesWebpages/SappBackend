
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
import pandas as pd
from rest_framework.permissions import IsAuthenticated

from accounts.models import Student
from accounts.serializers import StudentProfileSerializer,FacultyProfileSerializer, SOProfileSerializer

from general.utils.permissions import IsFaculty,IsOfficeAdmin,IsStudent



class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the profile data for the logged-in student or faculty."""
        # For logged-in student
        student = request.user.student_profile
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Update the profile data for the logged-in user or a student (if faculty)."""
        student_code = kwargs.get('student_code', None)  # Use student_code instead of student_id

        # Check if the request is for a specific student (only faculty can update student data)
        if student_code:
            # Ensure the user is a faculty member to update student data
            if request.user.role != 'faculty':
                raise PermissionDenied(detail="Only faculty can update student profiles. But good job! You have skills at finding exploits. Try to find and report it to the office admin.")

            # Attempt to find the student based on student_code
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Update the student profile
            serializer = StudentProfileSerializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If no student_code is provided, return an error
        return Response({"error": "Student code is required."}, status=status.HTTP_400_BAD_REQUEST)
    
'''class FacultyNavbarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the navbar data for the logged-in faculty."""
        faculty = request.user.faculty_profile
        serializer = FacultyNavbarSerializer(faculty)
        return Response(serializer.data)
'''

class FacultyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the profile data for the logged-in faculty."""
        faculty = request.user.faculty_profile
        serializer = FacultyProfileSerializer(faculty)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Update the profile data for the logged-in faculty and user."""
        faculty = request.user.faculty_profile
        serializer = FacultyProfileSerializer(faculty, data=request.data, partial=True)

        if serializer.is_valid():
            # Save the updated data
            serializer.save()

            # Return the updated data as response
            return Response(serializer.data)

        # Return errors if any occur during validation
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SOProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the profile data for the logged-in faculty."""
        admin = request.user.soadmin_profile
        serializer = SOProfileSerializer(admin)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Update the profile data for the logged-in faculty and user."""
        admin = request.user.soadmin_profile
        serializer = SOProfileSerializer(admin, data=request.data, partial=True)

        if serializer.is_valid():
            # Save the updated data
            serializer.save()

            # Return the updated data as response
            return Response(serializer.data)

        # Return errors if any occur during validation
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    


