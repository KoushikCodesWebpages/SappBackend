from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from students.models import StudentsDB
from faculties.models import FacultyDB

from accounts.serializers import  UserSerializer
from students.serializers import StudentsDBSerializer
from faculties.serializers import FacultyDBSerializer
from features.serializers import ProfileSerializer




from general.utils.base_view import BaseDBView


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