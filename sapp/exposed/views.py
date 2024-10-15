from rest_framework.permissions import  AllowAny

from accounts.models import Standard,  Section, Subject

from exposed.serializers import StandardSerializer, SectionSerializer,SubjectSerializer

from general.utils.pagination import CustomPagination, StandardPagination,SubjectPagination
from general.utils.base_view import BaseDBView


class StandardView(BaseDBView):
    model_class = Standard
    serializer_class = StandardSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]
    
class SubjectView(BaseDBView):
    model_class = Subject
    serializer_class = SubjectSerializer
    pagination_class = SubjectPagination
    permission_classes = [AllowAny]

class SectionView(BaseDBView):
    model_class = Section
    serializer_class = SectionSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
