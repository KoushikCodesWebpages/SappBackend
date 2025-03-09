from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils.http import http_date
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime




from features.models import Result, ResultLock
from features.serializers import ResultSerializer, ResultLockSerializer
from general.utils.permissions import IsFaculty, IsStudent, IsOfficeAdmin


class ResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow students and faculty to view results
            return [IsAuthenticated(), (IsStudent | IsFaculty | IsOfficeAdmin)()]
        elif self.request.method in ['POST', 'PUT', 'PATCH']:
            # Only faculty and school admins can create or update results
            return [IsAuthenticated(), (IsFaculty | IsOfficeAdmin)()]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='student').exists():
            # Students can only view their own results
            results = Result.objects.filter(student__user=user)
        else:
            # Faculty and school admins can view all results
            results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ResultSerializer(data=request.data)

        if serializer.is_valid():
            # Check if the result lock is active (for faculty)
            if user.groups.filter(name='faculty').exists():
                result_lock = serializer.validated_data.get('result_lock')
                if not result_lock.is_active():
                    return Response(
                        {"detail": "Results can only be added during the active result lock period."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            result = Result.objects.get(pk=pk)
        except Result.DoesNotExist:
            return Response(
                {"detail": "Result not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultSerializer(result, data=request.data, partial=False)

        if serializer.is_valid():
            # Check if the result lock is active (for faculty)
            if user.groups.filter(name='faculty').exists():
                result_lock = serializer.validated_data.get('result_lock')
                if not result_lock.is_active():
                    return Response(
                        {"detail": "Results can only be updated during the active result lock period."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            result = Result.objects.get(pk=pk)
        except Result.DoesNotExist:
            return Response(
                {"detail": "Result not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultSerializer(result, data=request.data, partial=True)

        if serializer.is_valid():
            # Check if the result lock is active (for faculty)
            if user.groups.filter(name='faculty').exists():
                result_lock = serializer.validated_data.get('result_lock')
                if not result_lock.is_active():
                    return Response(
                        {"detail": "Results can only be updated during the active result lock period."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ResultLockView(generics.ListCreateAPIView):
    """
    Handles listing and creating result locks.
    - `OfficeAdmin` can create (`POST`).
    - `Faculty` and `Students` can view (`GET`).
    - Implements `If-Modified-Since` and `ETag` for efficient polling.
    """
    queryset = ResultLock.objects.all()
    serializer_class = ResultLockSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOfficeAdmin()]
        return [IsAuthenticated(), (IsFaculty | IsOfficeAdmin())] 

    def get_queryset(self):
        """
        Filters result locks based on `If-Modified-Since` for polling.
        """
        last_modified = self.request.headers.get("If-Modified-Since")
        if last_modified:
            try:
                timestamp = make_aware(parse_datetime(last_modified))
                return ResultLock.objects.filter(last_updated__gt=timestamp)  # Fetch only updated records
            except (ValueError, TypeError):
                pass  # Ignore invalid timestamps and return all records
        return ResultLock.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Overrides the default list method to return `304 Not Modified`
        if no new/updated records are found.
        """
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response(status=status.HTTP_304_NOT_MODIFIED)  # No changes, return 304

        serializer = self.get_serializer(queryset, many=True)
        last_updated = queryset.order_by("-last_updated").first().last_updated  # Get most recent update time

        # Generate ETag based on last_updated timestamp
        etag_value = f'"{last_updated.timestamp()}"'

        # Check If-None-Match to prevent unnecessary data transfer
        if request.headers.get("If-None-Match") == etag_value:
            return Response(status=status.HTTP_304_NOT_MODIFIED)

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response["Last-Modified"] = http_date(last_updated.timestamp())  # Format timestamp
        response["ETag"] = etag_value  # Set ETag header
        return response


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
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsOfficeAdmin()]
        return [IsAuthenticated()]  # Faculty & students can view
