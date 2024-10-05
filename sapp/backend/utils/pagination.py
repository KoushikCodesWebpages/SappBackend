from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 12  # Adjust as needed

class SectionPagination(PageNumberPagination):
    page_size = 6

class StandardPagination(PageNumberPagination):
    page_size = 12 
    
class SubjectPagination(PageNumberPagination):
    page_size = 6     