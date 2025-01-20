import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Student, Faculty, OfficeAdmin
from .serializers import StudentNavbarSerializer,StudentProfileSerializer,FacultyNavbarSerializer,FacultyProfileSerializer



class ExcelUploadView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the file is a CSV or Excel file
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)  # Read CSV file
            elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file, engine='openpyxl')  # For Excel files (.xlsx)
            else:
                return Response({"error": "Unsupported file type. Only CSV and Excel files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

            # Process the data (example: iterate through the rows to create users)
            for index, row in df.iterrows():
                role = row.get('role')
                if not role or role not in ['student', 'faculty', 'office_admin']:
                    return Response({"error": f"Invalid role at row {index+1}"}, status=status.HTTP_400_BAD_REQUEST)

                if role == 'student':
                    self.create_student(row, index)
                elif role == 'faculty':
                    self.create_faculty(row, index)
                elif role == 'office_admin':
                    self.create_office_admin(row, index)

            return Response({"message": "Data uploaded successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_student(self, row, index):
        try:
            user_data = {
                'username': row['username'],
                'email': row['email'],
                'role': 'student',
                'password': make_password(row['password'])  # Hash the password
            }
            user = get_user_model().objects.create_user(**user_data)
            student_data = {
                'user': user,
                'enrollment_number': row['enrollment_number'],
                'standard': row['standard'],
                'section': row.get('section', ''),
                'subjects': row.get('subjects', []),
                'attendance_percent': row.get('attendance_percent', 0)
            }
            Student.objects.create(**student_data)

        except Exception as e:
            raise Exception(f"Error creating student at row {index+1}: {e}")

    def create_faculty(self, row, index):
        try:
            user_data = {
                'username': row['username'],
                'email': row['email'],
                'role': 'faculty',
                'password': make_password(row['password'])  # Hash the password
            }
            user = get_user_model().objects.create_user(**user_data)
            faculty_data = {
                'user': user,
                'faculty_id': row.get('faculty_id', ''),
                'department': row['department'],
                'specialization': row.get('specialization', ''),
                'coverage': row.get('coverage', []),
                'class_teacher': row.get('class_teacher', {})
            }
            Faculty.objects.create(**faculty_data)

        except Exception as e:
            raise Exception(f"Error creating faculty at row {index+1}: {e}")

    def create_office_admin(self, row, index):
        try:
            user_data = {
                'username': row['username'],
                'email': row['email'],
                'role': 'office_admin',
                'password': make_password(row['password'])  # Hash the password
            }
            user = get_user_model().objects.create_user(**user_data)
            office_admin_data = {
                'user': user,
                'employee_id': row.get('employee_id', ''),
                'school_name': row['school_name']
            }
            OfficeAdmin.objects.create(**office_admin_data)

        except Exception as e:
            raise Exception(f"Error creating office admin at row {index+1}: {e}")
        
        
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        # Get the username/email, password, and role from the request data
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')
        role = request.data.get('role')

        if not username_or_email or not password or not role:
            return Response({"error": "username_or_email, password, and role are required fields"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Attempt to authenticate with username or email
        user = None
        if '@' in username_or_email:  # Check if it's an email
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                user = get_user_model().objects.filter(email=username_or_email).first()
        else:
            user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            return Response({"error": "Invalid username/email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check the role of the user
        if user.role != role:
            return Response({"error": f"User role must be {role}"}, status=status.HTTP_403_FORBIDDEN)

        # Generate the JWT token for the user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Return the token in the response
        return Response({
            "access_token": str(access_token),
            "refresh_token": str(refresh)
        }, status=status.HTTP_200_OK)
        
        
class StudentNavbarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the navbar data for the logged-in student."""
        student = request.user.student_profile
        serializer = StudentNavbarSerializer(student)
        return Response(serializer.data)

class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the profile data for the logged-in student or faculty."""
        # For logged-in student
        student = request.user.student_profile
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Update the profile data for the logged-in user or a student (if faculty)."""
        student_code = kwargs.get('student_code', None)  # Use student_code instead of student_id

        # Check if the request is for a specific student (only faculty can update student data)
        if student_code:
            # Ensure the user is a faculty member to update student data
            if request.user.role != 'faculty':
                raise PermissionDenied(detail="Only faculty can update student profiles. But good job! You have skills at finding exploits. Try to find and report it to the office admin.")

            # Attempt to find the student based on student_code
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Update the student profile
            serializer = StudentProfileSerializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If no student_code is provided, return an error
        return Response({"error": "Student code is required."}, status=status.HTTP_400_BAD_REQUEST)
    
class FacultyNavbarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the navbar data for the logged-in faculty."""
        faculty = request.user.faculty_profile
        serializer = FacultyNavbarSerializer(faculty)
        return Response(serializer.data)

class FacultyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the profile data for the logged-in faculty."""
        faculty = request.user.faculty_profile
        serializer = FacultyProfileSerializer(faculty)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Update the profile data for the logged-in faculty and user."""
        faculty = request.user.faculty_profile
        serializer = FacultyProfileSerializer(faculty, data=request.data, partial=True)

        if serializer.is_valid():
            # Save the updated data
            serializer.save()

            # Return the updated data as response
            return Response(serializer.data)

        # Return errors if any occur during validation
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)