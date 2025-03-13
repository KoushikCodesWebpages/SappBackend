from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from features.models import CalendarEvent
from features.serializers import CalendarEventSerializer

from general.utils.permissions import IsFaculty,IsOfficeAdmin,IsStudent




class CalendarEventView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get_permissions(self):
        """Dynamically assign permissions based on request method."""
        if self.request.method == "POST":
            # Only office_admin can create an event
            return [IsAuthenticated(), IsOfficeAdmin()]
        elif self.request.method == "GET":
            # Any authenticated user can view events
            return [IsAuthenticated()]
        elif self.request.method == "DELETE":
            # Only office_admin can delete an event
            return [IsAuthenticated(), IsOfficeAdmin()]

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
        serializer = CalendarEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests: Only office admins can delete events.
        """
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