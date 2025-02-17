import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
import pandas as pd
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import AuthUser, Student, Faculty, SOAdmin
from .serializers import StudentSerializer,FacultySerializer,OfficeAdminSerializer

from general.utils.permissions import IsFaculty,IsOfficeAdmin,IsStudent



class ExcelUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read the uploaded file (CSV or Excel)
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)  # Read CSV file
            elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file, engine='openpyxl')  # For Excel files (.xlsx)
            else:
                return Response({"error": "Unsupported file type. Only CSV and Excel files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate through the rows and create users based on role
            for index, row in df.iterrows():
                role = row.get('role')
                if not role or role not in ['student', 'faculty', 'so_admin']:
                    return Response({"error": f"Invalid role at row {index+1}"}, status=status.HTTP_400_BAD_REQUEST)

                if role == 'student':
                    self.create_student(row, index)
                elif role == 'faculty':
                    self.create_faculty(row, index)
                elif role == 'so_admin':
                    self.create_office_admin(row, index)

            return Response({"message": "Data uploaded successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_student(self, row, index):
        try:
            # Create the user object with the plain password
            user_data = {
                'username': row['username'],
                'email': row['email'],
                'role': 'student',
                'password': row['password']  # Store the plain password first
            }

            # Create the user and hash the password
            user = get_user_model().objects.create_user(**user_data)

            # Now, hash the password using set_password (this is done automatically by create_user)
            # But you can call it manually if you want to, like this:
            user.set_password(row['password'])
            user.save()  # Save the user after setting the hashed password

            # Generate the student_code in the format email-standard-section
            student_code = f"{row['email']}-{row['standard']}-{row.get('section', '')}-{row['academic_year']}"

            # Create the related Student model
            student_data = {
                'user': user,
                'enrollment_number': row['enrollment_number'],
                'standard': row['standard'],
                'section': row.get('section', ''),  # Optional field
                'subjects': row.get('subjects', []),  # Optional field
                'attendance_percent': row.get('attendance_percent', 0),  # Optional field
                'student_code': student_code,  # Set the generated student_code
                'academic_year': row.get('academic_year'),
            }

            Student.objects.create(**student_data)

        except Exception as e:
            print(f"Error creating student: {e}")

    def create_faculty(self, row, index):
        try:
            # Hash the password before creating the user
             # Hash the password
            user_data = {
                'username': row['username'],
                'email': row['email'],
                'role': 'faculty',
                'password': row['password']  # Store the hashed password
            }
            user = get_user_model().objects.create_user(**user_data)
            user.set_password(row['password'])
            user.save() 

            # Create the related Faculty model
            faculty_data = {
                'user': user,
                'faculty_id': row.get('faculty_id', ''),  # Optional field
                'department': row['department'],
                'specialization': row.get('specialization', ''),  # Optional field
                'coverage': row.get('coverage', []),  # Optional field
                'class_teacher': row.get('class_teacher', {})  # Optional field
            }
            Faculty.objects.create(**faculty_data)

        except Exception as e:
            raise Exception(f"Error creating faculty at row {index+1}: {e}")

    def create_office_admin(self, row, index):
        try:
            # Hash the password before creating the user
            hashed_password = make_password(row['password'])  # Hash the password
            user_data = {
                'username': row['username'],
                'email': row['email'],
                'role': 'so_admin',
                'password': row['password']  # Store the hashed password
            }
            user = get_user_model().objects.create_user(**user_data)
            user.set_password(row['password'])
            user.save() 

            # Create the related OfficeAdmin model
            office_admin_data = {
                'user': user,
                'employee_id': row.get('employee_id', ''),  # Optional field
                'school_name': row['school_name']
            }
            SOAdmin.objects.create(**office_admin_data)

        except Exception as e:
            raise Exception(f"Error creating office admin at row {index+1}: {e}")


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get the email, password, and role from the request data
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        # Validate input
        if not email or not password or not role:
            return Response({"error": "email, password, and role are required fields"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Try to get the user by email
        user = get_user_model().objects.filter(email=email).first()

        if not user:
            return Response({"error 1": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check password manually
        if not user.check_password(password):
            return Response({"error 2": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the user has the required role
        if user.role != role:
            return Response({"error": f"User role must be {role}"}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT token for the authenticated user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Return the JWT tokens
        return Response({
            "access_token": str(access_token),
        }, status=status.HTTP_200_OK)

        
        
'''class StudentNavbarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Fetch the navbar data for the logged-in student."""
        student = request.user.student_profile
        serializer = StudentNavbarSerializer(student)
        return Response(serializer.data)
'''


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsOfficeAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['standard', 'section','academic_year']# Only SOAdmin can access

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated,  IsOfficeAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['faculty_id','department','specialization']# Only SOAdmin can access

class OfficeAdminViewSet(viewsets.ModelViewSet):
    queryset = SOAdmin.objects.all()
    serializer_class = OfficeAdminSerializer
    permission_classes = [IsAuthenticated,  IsOfficeAdmin]