from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from features.models import Timetable
from features.serializers import TimetableSerializer 



class TimetableView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Handle GET, POST, PUT, and DELETE requests for Timetable objects.
    """
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: Any authenticated user can fetch timetables.
        """
        try:
            # Apply filters for standard "7" and section "C"
            standard = request.query_params.get('standard', None)
            section = request.query_params.get('section', None)

            # Filtering based on query parameters
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
        Handle POST requests: Only office_admins can create timetables.
        """
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can create timetables."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TimetableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.username)  # Log the admin creating the timetable
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests: Only office_admins can update timetables.
        """
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can update timetables."}, status=status.HTTP_403_FORBIDDEN)

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
        Handle DELETE requests: Only office_admins can delete timetables.
        """
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response(
                {'detail': 'You do not have permission to delete timetables.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
 