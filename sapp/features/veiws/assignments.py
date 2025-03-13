from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from general.utils.permissions import IsFaculty, IsStudent
from features.models import Assignment
from features.serializers import AssignmentSerializer
from accounts.models import Faculty


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignments:
    - Faculty can **create, update, and delete** assignments.
    - Faculty and students can **retrieve** assignments.
    - Supports filtering by `section` and `standard`.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = "id"

    def get_permissions(self):
        """Set permissions dynamically for each action."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsFaculty()]  # Only faculty can modify
        return [IsAuthenticated(), permissions.OR(IsFaculty(), IsStudent())]  # Faculty & students can view

    def get_queryset(self):
        """Filter assignments by `section` and `standard`."""
        queryset = Assignment.objects.all()
        section = self.request.query_params.get("section")
        standard = self.request.query_params.get("standard")

        if section:
            queryset = queryset.filter(section=section)
        if standard:
            queryset = queryset.filter(standard=standard)

        return queryset

    def perform_create(self, serializer):
        """Ensure that only faculty can create assignments."""
        faculty = get_object_or_404(Faculty, user=self.request.user)
        serializer.save(faculty=faculty)

    def perform_update(self, serializer):
        """Ensure only the faculty who created the assignment can update it."""
        assignment = self.get_object()
        if assignment.faculty.user != self.request.user:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure only the faculty who created the assignment can delete it."""
        if instance.faculty.user != self.request.user:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
