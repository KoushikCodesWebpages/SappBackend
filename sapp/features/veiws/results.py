from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import serializers

from features.models import Result, ResultLock
from features.serializers import ResultSerializer, ResultLockSerializer
from general.utils.permissions import IsFaculty, IsStudent, IsOfficeAdmin

class ResultLockView(generics.ListCreateAPIView):
    queryset = ResultLock.objects.all()
    serializer_class = ResultLockSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsOfficeAdmin()]
        return [permissions.IsAuthenticated(), permissions.OR(IsFaculty(), IsOfficeAdmin())]  

    def get_queryset(self):
        """
        Since ETag and If-Modified-Since are handled by middleware, we simply return the queryset.
        """
        return ResultLock.objects.all().order_by('last_updated')

class ResultLockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a single result lock.
    - `GET` allowed for all authenticated users (`Faculty` & `Students`).
    - `PUT/PATCH` only for `OfficeAdmin` (modifications restricted).
    - `DELETE` only for `OfficeAdmin`.
    """
    queryset = ResultLock.objects.all()
    serializer_class = ResultLockSerializer

    def get_permissions(self):
        """Restrict modification to `OfficeAdmin`, allow all authenticated users to view."""
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated(), IsOfficeAdmin()]
        return [permissions.IsAuthenticated()]


class StudentResultAPIView(generics.ListAPIView):
    """
    API for students to retrieve their own results.
    """
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Result.objects.filter(student__user=self.request.user)
    

class FacultyResultView(generics.ListCreateAPIView,generics.RetrieveUpdateDestroyAPIView):
    """
    API for faculty to manage results.
    - GET: Retrieve results (filtered dynamically by any field)
    - POST: Create new results (only during active result lock)
    - PUT/PATCH: Update results (only during active result lock)
    - DELETE: Delete results
    """
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, IsFaculty]
    lookup_field = 'pk'

    def get_queryset(self):
        """Dynamically filters results based on any query parameter."""
        queryset = Result.objects.all()
        query_params = self.request.query_params

        filters = Q()
        for field, value in query_params.items():
            if hasattr(Result, field) or field.startswith("student__"):  # Ensures field exists
                filters &= Q(**{field: value})

        return queryset.filter(filters)

    def perform_create(self, serializer):
        """Checks result lock before creating results."""
        self._validate_result_lock(serializer)
        serializer.save()

    def perform_update(self, serializer):
        """Checks result lock before updating results."""
        self._validate_result_lock(serializer)
        serializer.save()

    def perform_destroy(self, instance):
        """Allows deletion of results (only for faculty & admin)."""
        instance.delete()

    def _validate_result_lock(self, serializer):
        """Validates if result modifications are allowed."""
        user = self.request.user
        if user.groups.filter(name="faculty").exists():
            result_lock = serializer.validated_data.get("result_lock")
            if not result_lock.is_active():
                raise serializers.ValidationError(
                    {"detail": "Results can only be modified during the active result lock period."}
                )


