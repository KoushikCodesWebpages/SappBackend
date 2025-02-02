from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from features.models import Announcement
from features.serializers import AnnouncementMainSerializer,AnnouncementDetailedSerializer



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
    # POST: Create a new announcement
    def post(self, request):
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can create announcements."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AnnouncementDetailedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.username)  # Log the admin creating the announcement
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
        if not self.is_office_admin(request.user):  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can delete announcements."}, status=status.HTTP_403_FORBIDDEN)

        try:
            announcement = Announcement.objects.get(pk=pk)
            announcement.delete()
            return Response({"message": "Announcement deleted successfully."}, status=status.HTTP_200_OK)
        except Announcement.DoesNotExist:
            return Response({"error": "Announcement not found."}, status=status.HTTP_404_NOT_FOUND)
 