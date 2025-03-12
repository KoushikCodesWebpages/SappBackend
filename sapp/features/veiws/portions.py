from rest_framework import viewsets,permissions
from rest_framework.permissions import IsAuthenticated
from general.utils.permissions import IsFaculty, IsStudent

from ..models import Portion
from ..serializers import PortionSerializer


class PortionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Portions:
    - Students **must** filter by both `standard` and `academic_year`.
    - Faculty can retrieve all portions or filter as needed.
    """
    serializer_class = PortionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = "id"

    def get_permissions(self):
        """Set permissions dynamically based on action."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), permissions.OR(IsFaculty() , IsStudent())]
        return [IsAuthenticated(), IsFaculty()]

    def get_queryset(self):
        """Customize queryset based on user role and filters."""
        queryset = Portion.objects.all()
        standard = self.request.query_params.get('standard')
        academic_year = self.request.query_params.get('academic_year')

        # Faculty can filter or get all portions
        if self.request.user.role == 'faculty':
            return queryset

        # Students MUST provide both standard & academic_year
        if self.request.user.role == 'student':
            if not standard or not academic_year:
                self.permission_denied(
                    self.request, message="Students must filter by both standard and academic_year."
                )
            return queryset.filter(standard=standard, academic_year=academic_year)

        return queryset  # Fallback for other user roles (if any)
