from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from features.models import CalendarEvent
from features.serializers import CalendarEventSerializer




class CalendarEventView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: Any authenticated user can fetch the events.
        """
        try:
            events = CalendarEvent.objects.all()
            serializer = CalendarEventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': f'Error fetching events: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can create announcements."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CalendarEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.username)  # Log the admin creating the announcement
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests: Only office admins can delete events.
        """
        # Check if the user is an office admin
        if request.user.role != 'office_admin':
            return Response(
                {'detail': 'You do not have permission to delete events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event_id = kwargs.get('pk')
        try:
            event = CalendarEvent.objects.get(id=event_id)
            event.delete()
            return Response({'detail': 'Event deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except CalendarEvent.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': f'Error deleting event: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
  