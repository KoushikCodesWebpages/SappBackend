from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils.http import http_date
from django.http import HttpResponseNotModified
from django.utils.timezone import is_naive, make_aware
from django.utils.http import parse_http_date_safe, http_date
from django.http import HttpResponseNotModified
from django.utils.timezone import make_aware, is_naive
from datetime import datetime, timezone
import math

from features.models import Result, ResultLock
from features.serializers import ResultSerializer, ResultLockSerializer
from general.utils.permissions import IsFaculty, IsStudent, IsOfficeAdmin

class ResultLockView(generics.ListCreateAPIView):
    queryset = ResultLock.objects.all()
    serializer_class = ResultLockSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOfficeAdmin()]
        return [IsAuthenticated(), permissions.OR(IsFaculty(), IsOfficeAdmin())]  

    def get_queryset(self):
        last_modified = self.request.headers.get("If-Modified-Since")

        if not last_modified:
            print("⚠️ No If-Modified-Since header received. Returning all data.")
            return ResultLock.objects.all()

        print(f"✅ Received If-Modified-Since header (raw): {last_modified}")

        try:
            timestamp = parse_http_date_safe(last_modified)

            if timestamp is None:
                print(f"❌ Failed to parse If-Modified-Since: {last_modified}")
                return ResultLock.objects.all()

            timestamp_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
            
            # Fix 1: Remove microsecond errors
            timestamp_seconds = math.floor(timestamp_dt.timestamp())  # Floor to seconds
            timestamp_dt = datetime.utcfromtimestamp(timestamp_seconds).replace(tzinfo=timezone.utc)

            print(f"🔍 Filtering for updates after: {timestamp_dt}")

            queryset = ResultLock.objects.filter(last_updated__gt=timestamp_dt)
            print(f"🔍 Filtered Queryset Count: {queryset.count()}")

            return queryset  

        except Exception as e:
            print(f"❌ Error processing If-Modified-Since: {e}")
            return ResultLock.objects.all()  

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not queryset.exists():
            print("✅ No new data → Returning 304 Not Modified")
            return HttpResponseNotModified()

        serializer = self.get_serializer(queryset, many=True)
        last_updated = queryset.order_by("-last_updated").first().last_updated  

        if is_naive(last_updated):
            last_updated = make_aware(last_updated)

        # Fix 2: Use milliseconds to avoid floating-point mismatches
        etag_value = f'"{int(last_updated.timestamp() * 1000)}"'  

        client_etag = request.headers.get("If-None-Match")
        print(f"📌 Received If-None-Match: {client_etag}, Calculated ETag: {etag_value}")

        if client_etag == etag_value:
            print("✅ ETag matched → Returning 304 Not Modified")
            return HttpResponseNotModified()

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response["Last-Modified"] = http_date(last_updated.timestamp())  
        response["ETag"] = etag_value  

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
        """Restrict modification to `OfficeAdmin`, allow all authenticated users to view."""
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated(), IsOfficeAdmin()]
        return [permissions.IsAuthenticated()]



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
    


