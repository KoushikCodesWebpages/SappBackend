from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from features.models import Timetable
from features.serializers import TimetableSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from general.utils.permissions import IsFaculty, IsStudent, IsOfficeAdmin # Assuming you have these custom permissions

class TimetableView(APIView):
    """
    Handle GET, POST, PUT, and DELETE requests for Timetable objects.
    """
    def get_permissions(self):
        """Dynamically assign permissions based on request method."""
        if self.request.method in ["POST", "PUT"]:
            return [permissions.IsAuthenticated(), IsOfficeAdmin()]  # Only Faculty can create/update
        elif self.request.method == "GET":
            return [permissions.IsAuthenticated()]  # Faculty & Students can view
        return [permissions.IsAuthenticated()]  # Default case (shouldn't happen)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: Any authenticated Faculty or Student can fetch timetables.
        """
        try:
            # Apply filters for standard and section if provided
            standard = request.query_params.get('standard', None)
            section = request.query_params.get('section', None)

            timetables = Timetable.objects.all()
            if standard:
                timetables = timetables.filter(standard=standard)
            if section:
                timetables = timetables.filter(section=section)

            serializer = TimetableSerializer(timetables, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': f'Error fetching timetables: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Handle POST requests: Only Faculty can create timetables.
        """
        serializer = TimetableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.username)  # Log the faculty creating the timetable
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests: Only Faculty can update timetables.
        """
        timetable_id = kwargs.get('pk')
        try:
            timetable = Timetable.objects.get(id=timetable_id)
            serializer = TimetableSerializer(timetable, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()  # Save the updates
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Timetable.DoesNotExist:
            return Response({'detail': 'Timetable not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': f'Error updating timetable: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests: Only Faculty can delete timetables.
        """
        timetable_id = kwargs.get('pk')
        try:
            timetable = Timetable.objects.get(id=timetable_id)
            timetable.delete()
            return Response({'detail': 'Timetable deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Timetable.DoesNotExist:
            return Response({'detail': 'Timetable not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': f'Error deleting timetable: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
