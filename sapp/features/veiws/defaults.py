from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.models import Student,Faculty, AuthUser
from rest_framework import status

class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_students = Student.objects.count()
        total_verified_accounts = AuthUser.objects.filter(is_verified=False).count()  # Assuming 'is_verified' field
        total_teachers = Faculty.objects.count()
        #total_complaints = Complaint.objects.count()

        data = {
            "total_students": total_students,
            "total_unverified_accounts": total_verified_accounts,
            "total_teachers": total_teachers,
            #"total_complaints": total_complaints,
        }

        return Response(data)
    
    
class FilterStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Filter students based on standard and section."""
        # Get the standard and section from the request query parameters
        standard_section = request.query_params.get('class', None)

        # Validate the input
        if not standard_section:
            return Response({"error": "class parameter is required. Format: ['7', 'C']"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            standard, section = eval(standard_section)  # Safely parse the input list
            if not (isinstance(standard, str) and isinstance(section, str)):
                raise ValueError
        except (ValueError, SyntaxError):
            return Response({"error": "Invalid format for class. Format should be ['standard', 'section']"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Query the students based on standard and section
        students = Student.objects.filter(standard=standard, section=section).values('student_code', 'user__username')
        
        # Return the filtered students
        return Response(list(students), status=status.HTTP_200_OK)
