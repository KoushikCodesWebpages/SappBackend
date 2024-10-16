from rest_framework.permissions import IsAuthenticated, AllowAny

from faculties.models import FacultyDB

from faculties.serializers import FacultyDBSerializer

from general.utils.pagination import CustomPagination, SectionPagination, StandardPagination,SubjectPagination
from general.utils.base_view import BaseDBView






class FacultyDbView(BaseDBView):
    model_class = FacultyDB
    serializer_class = FacultyDBSerializer
    permission_classes = [AllowAny]  # Only authenticated users can access this view
    pagination_class = CustomPagination
