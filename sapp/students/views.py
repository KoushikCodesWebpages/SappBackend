from rest_framework.permissions import IsAuthenticated, AllowAny

from students.models import StudentsDB

from students.serializers import StudentsDBSerializer

from general.utils.pagination import CustomPagination
from general.utils.base_view import BaseDBView



class StudentsDbView(BaseDBView):
    model_class = StudentsDB
    serializer_class = StudentsDBSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination