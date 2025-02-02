from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from general.utils.permissions import IsFaculty

from general.utils.permissions import IsFaculty, IsStudent

from ..models import Portion
from ..serializers import PortionSerializer

class PortionView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get_permissions(self):
        """
        Apply permissions for the view actions.
        """
        if self.request.method == 'GET':
            # Students and Faculty can retrieve portions
            return [IsAuthenticated(), (IsFaculty() | IsStudent())]
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Only Faculty can create, update, or delete portions
            return [IsAuthenticated(), IsFaculty()]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """
        Retrieve portions based on user role and optional filters:
        - Students can view portions for their standard and academic year.
        - Faculty can view all portions, optionally filtered by standard and academic year.
        """
        # Get query parameters for filtering
        standard = request.query_params.get('standard', None)
        academic_year = request.query_params.get('academic_year', None)

        # Base queryset
        queryset = Portion.objects.all()

        # Apply filters based on query parameters
        if standard:
            queryset = queryset.filter(standard=standard)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        # Additional restrictions for students
        if request.user.role == 'student':
            if not standard or not academic_year:
                return Response(
                    {'detail': 'Both standard and academic_year are required for students.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Serialize and return the data
        serializer = PortionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a new portion. Only faculty can create portions.
        """
        serializer = PortionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new portion
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, portion_id, *args, **kwargs):
        """
        Update an entire portion. Only faculty can update portions.
        """
        try:
            portion = Portion.objects.get(id=portion_id)
        except Portion.DoesNotExist:
            return Response({'detail': 'Portion not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PortionSerializer(portion, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated portion
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, portion_id, *args, **kwargs):
        """
        Partially update a portion. Only faculty can update portions.
        """
        try:
            portion = Portion.objects.get(id=portion_id)
        except Portion.DoesNotExist:
            return Response({'detail': 'Portion not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PortionSerializer(portion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the partially updated portion
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, portion_id, *args, **kwargs):
        """
        Delete a portion. Only faculty can delete portions.
        """
        try:
            portion = Portion.objects.get(id=portion_id)
        except Portion.DoesNotExist:
            return Response({'detail': 'Portion not found.'}, status=status.HTTP_404_NOT_FOUND)

        portion.delete()  # Delete the portion
        return Response({'detail': 'Portion deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

