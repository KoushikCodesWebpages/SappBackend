from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from general.utils.permissions import IsFaculty

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
    
   
   
class ResultLockView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow faculty and school admins to view result locks
            return [IsAuthenticated(), (IsFaculty | IsOfficeAdmin)()]
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Only school admins can create, update, or delete result locks
            return [IsAuthenticated(), IsOfficeAdmin()]
        return super().get_permissions()

    def check_permissions(self, request):
        """
        Override to provide custom error messages for faculty attempting unauthorized actions.
        """
        super().check_permissions(request)  # Default permission checks

        # Custom error handling for faculty attempting POST, PUT, PATCH, or DELETE
        if request.user.groups.filter(name='faculty').exists() and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_denied(
                request,
                message="Faculty members are not allowed to perform this action.",
                code=status.HTTP_403_FORBIDDEN
            )

    def get(self, request, *args, **kwargs):
        result_locks = ResultLock.objects.all()
        serializer = ResultLockSerializer(result_locks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ResultLockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        try:
            result_lock = ResultLock.objects.get(pk=pk)
        except ResultLock.DoesNotExist:
            return Response(
                {"detail": "ResultLock not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultLockSerializer(result_lock, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        try:
            result_lock = ResultLock.objects.get(pk=pk)
        except ResultLock.DoesNotExist:
            return Response(
                {"detail": "ResultLock not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultLockSerializer(result_lock, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            result_lock = ResultLock.objects.get(pk=pk)
        except ResultLock.DoesNotExist:
            return Response(
                {"detail": "ResultLock not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        result_lock.delete()
        return Response(
            {"detail": "ResultLock deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        ) 
 