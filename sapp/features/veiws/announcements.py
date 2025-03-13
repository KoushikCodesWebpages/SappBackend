from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from features.models import Announcement
from features.serializers import AnnouncementMainSerializer,AnnouncementDetailedSerializer

from general.utils.permissions import IsFaculty,IsOfficeAdmin,IsStudent


class AnnouncementMainDisplayView(APIView):
    permission_classes = [IsAuthenticated] 
    """
    GET: Fetch the latest active announcement with minimal details.
    """
    def get(self, request):
        announcement = Announcement.get_latest_active()
        if announcement:
            serializer = AnnouncementMainSerializer(announcement)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "No active announcements at the moment."}, status=status.HTTP_404_NOT_FOUND)
    

class AnnouncementView(APIView):
    """
    POST: Create a new announcement (only office_admin role).
    GET: Fetch a detailed list of all announcements or an individual announcement by ID.
    DELETE: Delete an announcement by ID (only office_admin role).
    """

    def get_permissions(self):
        """Dynamically assign permissions based on request method."""
        if self.request.method == "POST":
            # Only office_admin can create an announcement
            return [IsAuthenticated(), IsOfficeAdmin()]
        elif self.request.method == "GET":
            # Both faculty and students can view announcements
            return [IsAuthenticated()]

        elif self.request.method == "DELETE":
            # Only office_admin can delete an announcement
            return [IsAuthenticated(), IsOfficeAdmin()]
        return [IsAuthenticated()]  # Default case (shouldn't happen)

    # POST: Create a new announcement
    def post(self, request):
        # The permission check is already handled dynamically in get_permissions(), so no need to check here
        serializer = AnnouncementDetailedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Log the admin creating the announcement
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET: Fetch all announcements or an individual announcement by ID
    def get(self, request, pk=None):
        if pk:
            # Fetch individual announcement by ID
            try:
                announcement = Announcement.objects.get(pk=pk)
                serializer = AnnouncementDetailedSerializer(announcement)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Announcement.DoesNotExist:
                return Response({"error": "Announcement not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all announcements (list view)
            announcements = Announcement.objects.all()
            serializer = AnnouncementDetailedSerializer(announcements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE: Delete an announcement by ID
    def delete(self, request, pk=None):
        # The permission check is already handled dynamically in get_permissions(), so no need to check here
        try:
            announcement = Announcement.objects.get(pk=pk)
            announcement.delete()
            return Response({"message": "Announcement deleted successfully."}, status=status.HTTP_200_OK)
        except Announcement.DoesNotExist:
            return Response({"error": "Announcement not found."}, status=status.HTTP_404_NOT_FOUND)
