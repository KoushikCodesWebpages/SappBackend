from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from general.utils.permissions import IsFaculty
from rest_framework.exceptions import PermissionDenied
from datetime import date

from accounts.models import Student
from .models import Attendance,AttendanceLock

from features.serializers import AttendanceLockSerializer, AttendanceSerializer


class AttendanceLockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET: Return the latest AttendanceLock for the current date.
        Allowed for faculty and office roles only.
        """
        if request.user.role in ['faculty', 'office_admin']:
            today = date.today()
            try:
                attendance_lock = AttendanceLock.objects.filter(date=today).latest('id')
                serializer = AttendanceLockSerializer(attendance_lock)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except AttendanceLock.DoesNotExist:
                return Response({"detail": "No attendance lock found for today."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        """
        POST: Create a new AttendanceLock entry for a specific date.
        Allowed for office role only.
        """
        if request.user.role == 'office_admin':
            # Ensure only one AttendanceLock per date
            date_to_lock = request.data.get('date')
            if AttendanceLock.objects.filter(date=date_to_lock).exists():
                return Response({"detail": "Attendance lock for this date already exists."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = AttendanceLockSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
    def put(self, request):
        """
        PUT: Update the 'is_locked' field of an existing AttendanceLock.
        Allowed for office role only, and only when 'is_locked' is currently false.
        """
        if request.user.role == 'office_admin':
            date_to_update = request.data.get('date')
            try:
                # Find the record for the specified date
                attendance_lock = AttendanceLock.objects.get(date=date_to_update)

                # Check if `is_locked` is currently false
                if not attendance_lock.is_locked:
                    serializer = AttendanceLockSerializer(attendance_lock, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"detail": "Attendance lock is already true; no updates allowed."}, status=status.HTTP_400_BAD_REQUEST)
            
            except AttendanceLock.DoesNotExist:
                return Response({"detail": "Attendance lock for this date does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

class AttendanceDaysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET: Retrieve all locked (working days) and unlocked (non-working days) dates.
        Allowed for faculty and office roles only.
        """
        if request.user.role in ['faculty', 'office_admin']:
            # Query the AttendanceLock model
            locked_days = AttendanceLock.objects.filter(is_locked=True).values_list('date', flat=True)
            unlocked_days = AttendanceLock.objects.filter(is_locked=False).values_list('date', flat=True)

            return Response({
                "working_days": list(locked_days),
                "non_working_days": list(unlocked_days)
            }, status=status.HTTP_200_OK)
        
        return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
    
    
class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Post attendance for multiple students. Only faculty members can create attendance records.
        """
        if request.user.role != 'faculty':
            return Response({'detail': 'You do not have permission to create attendance records.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Check if data is a list of attendance records
        if isinstance(request.data, list):
            attendance_objects = []  # List to hold Attendance objects to be created

            for record in request.data:
                student_code = record.get('student')
                date = record.get('date')
                status_value = record.get('status')

                # Look up the student based on student_code
                try:
                    student = Student.objects.get(student_code=student_code)
                except Student.DoesNotExist:
                    return Response({"detail": f"Student with student_code {student_code} does not exist."}, 
                                     status=status.HTTP_400_BAD_REQUEST)

                # Create the attendance object (without saving to DB yet)
                attendance = Attendance(
                    student=student,
                    date=date,
                    status=status_value
                )
                attendance_objects.append(attendance)  # Add to the list of objects to be created

            # Bulk create all attendance records at once
            Attendance.objects.bulk_create(attendance_objects)

            return Response({"message": "Attendance records created successfully"}, status=status.HTTP_201_CREATED)

        return Response({'detail': 'Invalid data format. Expected a list of attendance records.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Get attendance based on student standard and section, extracted from student_code.
        """
        standard = request.query_params.get('standard')
        section = request.query_params.get('section')

        if standard and section:
            # Filter attendance based on standard and section extracted from student_code
            attendance = Attendance.objects.filter(
                student__student_code__endswith=f"-{standard}-{section}"
            )
        else:
            attendance = Attendance.objects.all()

        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        Update attendance for multiple students. Only faculty members can update attendance records.
        """
        if request.user.role != 'faculty':
            return Response({'detail': 'You do not have permission to update attendance records.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Check if data is a list of attendance records
        if isinstance(request.data, list):
            updated_data = []
            for record in request.data:
                student_code = record.get('student_code')
                date = record.get('date')
                status = record.get('status')

                # Get the student based on student_code (assuming email-standard-section format)
                try:
                    student = Student.objects.get(student_code=student_code)
                except Student.DoesNotExist:
                    return Response({"detail": f"Student with student_code {student_code} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

                # Check if attendance record already exists for the given student and date
                attendance = Attendance.objects.filter(student=student, date=date).first()
                if attendance:
                    # Update the existing attendance record
                    attendance.status = status
                    attendance.save()
                    updated_data.append(AttendanceSerializer(attendance).data)
                else:
                    # Create a new attendance record if it doesn't exist
                    attendance_data = {
                        'student': student.id,  # Reference to the student model
                        'date': date,
                        'status': status
                    }
                    serializer = AttendanceSerializer(data=attendance_data)
                    if serializer.is_valid():
                        serializer.save()
                        updated_data.append(serializer.data)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(updated_data, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid data format. Expected a list of attendance records.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
'''def restrict_non_get_for_students(request):
    """
    Restrict non-GET requests for students.
    """
    user = request.user
    # If the user is a student and the request method is not GET
    if hasattr(user, 'student_profile') and request.method != 'GET':
        raise PermissionDenied("Students are only allowed to perform GET requests.")

    
class ProfileView(BaseDBView):
    serializer_class = ProfileSerializer  # Using ProfileSerializer for reading user profile
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile_data = {}

        # Fetch student profile
        try:
            student = StudentsDB.objects.get(user=user)
            profile_data['student_profile'] = StudentsDBSerializer(student).data
        except StudentsDB.DoesNotExist:
            profile_data['student_profile'] = None

        # Fetch faculty profile (not included in the response)
        try:
            faculty = FacultyDB.objects.get(user=user)  # Optional logic for faculty
        except FacultyDB.DoesNotExist:
            pass  # Do nothing if faculty doesn't exist

        return Response(profile_data)

    def patch(self, request):
        user = request.user
        profile_data = {}

        # Update student profile if it exists
        try:
            student = StudentsDB.objects.get(user=user)
            student_serializer = StudentsDBSerializer(student, data=request.data, partial=True)
            if student_serializer.is_valid(raise_exception=True):
                student_serializer.save()
                profile_data['student_profile'] = student_serializer.data
            else:
                return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentsDB.DoesNotExist:
            return Response({"error": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(profile_data)
    

class AssignmentView(BaseDBView):
    model_class = Assignment
    serializer_class = AssignmentSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        # Restrict non-GET requests for students
        restrict_non_get_for_students(request)
        return super().dispatch(request, *args, **kwargs)


class ResultView(BaseDBView):
    model_class = Result
    serializer_class = ResultSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        restrict_non_get_for_students(request)
        return super().dispatch(request, *args, **kwargs)


class ReportView(BaseDBView):
    model_class = Report
    serializer_class = ReportSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        restrict_non_get_for_students(request)
        return super().dispatch(request, *args, **kwargs)


class FeeView(BaseDBView):
    model_class = Fee
    serializer_class = FeeSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        restrict_non_get_for_students(request)
        return super().dispatch(request, *args, **kwargs)


class AttendanceView(BaseDBView):
    model_class = Attendance
    serializer_class = AttendanceSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        restrict_non_get_for_students(request)
        return super().dispatch(request, *args, **kwargs)


class TimetableView(BaseDBView):
    model_class = Timetable
    serializer_class = TimetableSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        restrict_non_get_for_students(request)
        return super().dispatch(request, *args, **kwargs)


class CalendarEventView(BaseDBView):
    model_class = CalendarEvent
    serializer_class = CalendarEventSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        restrict_non_get_for_students(request)
        return super().dispatch(request, *args, **kwargs)

    '''