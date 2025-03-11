from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from general.utils.permissions import IsFaculty
from features.models import Submission
from features.serializers import SubmissionSerializer, SubmissionMinSerializer
from general.utils.permissions import IsFaculty, IsStudent


from accounts.models import Student,Faculty
from django.shortcuts import get_object_or_404




class StudentSubmissionViewSet(viewsets.ModelViewSet):
    """
    API for students to manage their own submissions.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        """
        Students can only view, update, or delete their own submissions.
        """
        return Submission.objects.filter(student=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Custom list method to filter by assignment_id.
        """
        assignment_id = request.query_params.get("assignment_id")
        queryset = self.get_queryset().filter(assignment_id=assignment_id) if assignment_id else self.get_queryset()

        if not queryset.exists():
            return Response({"detail": "No submissions yet."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubmissionSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'list':
            return SubmissionSerializer
        return SubmissionSerializer
    
    
class FacultySubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for faculty to view all submissions for a specific assignment.
    """
    permission_classes = [IsAuthenticated, IsFaculty]
    serializer_class = SubmissionSerializer  # Faculty only needs minimal details

    def get_queryset(self):
        """
        Faculty can view all submissions for a given assignment.
        """
        assignment_id = self.request.query_params.get("assignment_id")
        if not assignment_id:
            return Submission.objects.none()  # Prevent fetching all if no assignment is specified

        queryset = Submission.objects.filter(assignment_id=assignment_id)
        if not queryset.exists():
            return Submission.objects.none()  # Ensures faculty gets an empty response if no submissions exist
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Return submissions for a given assignment or 'No submissions yet' if empty.
        """
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"detail": "No submissions yet."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)