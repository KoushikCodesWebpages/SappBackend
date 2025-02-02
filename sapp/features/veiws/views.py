'''from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from general.utils.permissions import IsFaculty
from datetime import date
from accounts.models import Student
from features.models import Attendance,AttendanceLock,Announcement,CalendarEvent,Timetable, Result, ResultLock, Assignment, Submission
from features.serializers import AttendanceLockSerializer, AttendanceSerializer, AnnouncementMainSerializer,AnnouncementDetailedSerializer,CalendarEventSerializer,TimetableSerializer, ResultSerializer, ResultLockSerializer, AssignmentSerializer, AssignmentMinSerializer, SubmissionSerializer, SubmissionMinSerializer
from general.utils.permissions import IsFaculty, IsStudent, IsOfficeAdmin


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
            Get attendance based on student standard and section, or by authenticated user's email.
            """
            email = request.query_params.get('email')
            standard = request.query_params.get('standard')
            section = request.query_params.get('section')

            # Check if the user is querying for their own attendance or faculty queries
            if email:
                # Verify if the email matches the authenticated user's email
                if email != request.user.email:
                    return Response({"detail": "You are not authorized to access this student's attendance."}, status=403)

                # Filter attendance based on the email part of student_code
                attendance = Attendance.objects.filter(
                    student__student_code__startswith=email
                )
            elif standard and section:
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
        


class AnnouncementMainDisplayView(APIView):
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
    
class CalendarEventView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: Any authenticated user can fetch the events.
        """
        try:
            events = CalendarEvent.objects.all()
            serializer = CalendarEventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': f'Error fetching events: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can create announcements."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CalendarEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.username)  # Log the admin creating the announcement
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests: Only office admins can delete events.
        """
        # Check if the user is an office admin
        if request.user.role != 'office_admin':
            return Response(
                {'detail': 'You do not have permission to delete events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event_id = kwargs.get('pk')
        try:
            event = CalendarEvent.objects.get(id=event_id)
            event.delete()
            return Response({'detail': 'Event deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except CalendarEvent.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': f'Error deleting event: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    
class TimetableView(APIView):
    """
    Handle GET, POST, PUT, and DELETE requests for Timetable objects.
    """
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: Any authenticated user can fetch timetables.
        """
        try:
            # Apply filters for standard "7" and section "C"
            standard = request.query_params.get('standard', None)
            section = request.query_params.get('section', None)

            # Filtering based on query parameters
            timetables = Timetable.objects.all()

            if standard:
                timetables = timetables.filter(standard=standard)
            if section:
                timetables = timetables.filter(section=section)

            serializer = TimetableSerializer(timetables, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'detail': f'Error fetching timetables: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Handle POST requests: Only office_admins can create timetables.
        """
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can create timetables."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TimetableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.username)  # Log the admin creating the timetable
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests: Only office_admins can update timetables.
        """
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response({"error": "Only office_admin can update timetables."}, status=status.HTTP_403_FORBIDDEN)

        timetable_id = kwargs.get('pk')
        try:
            timetable = Timetable.objects.get(id=timetable_id)
            serializer = TimetableSerializer(timetable, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()  # Save the updates
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Timetable.DoesNotExist:
            return Response({'detail': 'Timetable not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': f'Error updating timetable: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests: Only office_admins can delete timetables.
        """
        if not request.user.role == 'office_admin':  # Check if the user is an office_admin
            return Response(
                {'detail': 'You do not have permission to delete timetables.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        timetable_id = kwargs.get('pk')
        try:
            timetable = Timetable.objects.get(id=timetable_id)
            timetable.delete()
            return Response({'detail': 'Timetable deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Timetable.DoesNotExist:
            return Response({'detail': 'Timetable not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'detail': f'Error deleting timetable: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class ResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow students and faculty to view results
            return [IsAuthenticated(), (IsStudent | IsFaculty | IsOfficeAdmin)()]
        elif self.request.method in ['POST', 'PUT', 'PATCH']:
            # Only faculty and school admins can create or update results
            return [IsAuthenticated(), (IsFaculty | IsOfficeAdmin)()]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='student').exists():
            # Students can only view their own results
            results = Result.objects.filter(student__user=user)
        else:
            # Faculty and school admins can view all results
            results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ResultSerializer(data=request.data)

        if serializer.is_valid():
            # Check if the result lock is active (for faculty)
            if user.groups.filter(name='faculty').exists():
                result_lock = serializer.validated_data.get('result_lock')
                if not result_lock.is_active():
                    return Response(
                        {"detail": "Results can only be added during the active result lock period."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            result = Result.objects.get(pk=pk)
        except Result.DoesNotExist:
            return Response(
                {"detail": "Result not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultSerializer(result, data=request.data, partial=False)

        if serializer.is_valid():
            # Check if the result lock is active (for faculty)
            if user.groups.filter(name='faculty').exists():
                result_lock = serializer.validated_data.get('result_lock')
                if not result_lock.is_active():
                    return Response(
                        {"detail": "Results can only be updated during the active result lock period."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            result = Result.objects.get(pk=pk)
        except Result.DoesNotExist:
            return Response(
                {"detail": "Result not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultSerializer(result, data=request.data, partial=True)

        if serializer.is_valid():
            # Check if the result lock is active (for faculty)
            if user.groups.filter(name='faculty').exists():
                result_lock = serializer.validated_data.get('result_lock')
                if not result_lock.is_active():
                    return Response(
                        {"detail": "Results can only be updated during the active result lock period."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
   
   
class ResultLockView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow faculty and school admins to view result locks
            return [IsAuthenticated(), (IsFaculty | IsOfficeAdmin)()]
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Only school admins can create, update, or delete result locks
            return [IsAuthenticated(), IsOfficeAdmin()]
        return super().get_permissions()

    def check_permissions(self, request):
        """
        Override to provide custom error messages for faculty attempting unauthorized actions.
        """
        super().check_permissions(request)  # Default permission checks

        # Custom error handling for faculty attempting POST, PUT, PATCH, or DELETE
        if request.user.groups.filter(name='faculty').exists() and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_denied(
                request,
                message="Faculty members are not allowed to perform this action.",
                code=status.HTTP_403_FORBIDDEN
            )

    def get(self, request, *args, **kwargs):
        result_locks = ResultLock.objects.all()
        serializer = ResultLockSerializer(result_locks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ResultLockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        try:
            result_lock = ResultLock.objects.get(pk=pk)
        except ResultLock.DoesNotExist:
            return Response(
                {"detail": "ResultLock not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultLockSerializer(result_lock, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        try:
            result_lock = ResultLock.objects.get(pk=pk)
        except ResultLock.DoesNotExist:
            return Response(
                {"detail": "ResultLock not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResultLockSerializer(result_lock, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            result_lock = ResultLock.objects.get(pk=pk)
        except ResultLock.DoesNotExist:
            return Response(
                {"detail": "ResultLock not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        result_lock.delete()
        return Response(
            {"detail": "ResultLock deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        ) 
    
class AssignmentView(APIView):
    permission_classes = [IsAuthenticated]  # Default permission for authenticated users

    def get_permissions(self):
        """
        Apply permissions for the view actions.
        """
        if self.request.method == 'POST':
            # Only Faculty can create assignments
            return [IsAuthenticated(), IsFaculty()]
        if self.request.method in ['GET']:
            # Faculty and Students can retrieve assignments
            return [IsAuthenticated(), (IsFaculty() | IsStudent())]
        if self.request.method == 'DELETE':
            # Only Faculty can delete assignments
            return [IsAuthenticated(), IsFaculty()]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """
        Retrieve the assignments, filtered by `section` and `standard`.
        """
        section = request.query_params.get('section', None)
        standard = request.query_params.get('standard', None)

        # Filtering based on section and standard
        queryset = Assignment.objects.all()

        if section:
            queryset = queryset.filter(section=section)
        if standard:
            queryset = queryset.filter(standard=standard)

        # Use the minimal serializer for GET requests
        serializer = AssignmentMinSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a new assignment. Only faculty can create assignments.
        """
        # Faculty must be the creator
        if not request.user.role == 'faculty':
            return Response({'detail': 'Permission denied. Only faculty can create assignments.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Use the full serializer for POST requests
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(faculty=request.user)  # Assign faculty as the creator of the assignment
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, assignment_id, *args, **kwargs):
        """
        Delete an assignment. Only faculty can delete assignments.
        """
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({'detail': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the requesting user is the faculty who created the assignment
        if assignment.faculty != request.user:
            return Response({'detail': 'Permission denied. You can only delete assignments created by you.'},
                            status=status.HTTP_403_FORBIDDEN)

        assignment.delete()
        return Response({'detail': 'Assignment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
    
    
class SubmissionView(APIView):
    permission_classes = [IsAuthenticated]  # Default permission for authenticated users

    def get_permissions(self):
        """
        Apply permissions for the view actions.
        """
        if self.request.method == 'POST':
            # Only Students can create submissions
            return [IsAuthenticated(), IsStudent()]
        if self.request.method == 'GET':
            # Students can only get their own submissions
            return [IsAuthenticated(), (IsFaculty() | IsStudent())]
        return super().get_permissions()

    def get_queryset(self, student=None):
        """
        This method returns submissions, filtered by student if needed.
        """
        if student:
            return Submission.objects.filter(student=student)  # Only return the student's own submissions
        return Submission.objects.all()  # Faculty or others can get all submissions related to them

    def get(self, request, *args, **kwargs):
        """
        Retrieve submissions. Students can only view their own submissions.
        Faculty or others can view based on the data.
        """
        student = request.user if request.user.role == 'student' else None

        # If the user is a student, filter submissions by their own user data
        queryset = self.get_queryset(student=student)

        # Use the appropriate serializer based on the data.
        serializer = SubmissionMinSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a new submission. Only students can create submissions.
        """
        # Ensure the request is made by a student
        if request.user.role != 'student':
            return Response({'detail': 'Permission denied. Only students can create submissions.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Assign the student to the submission (since they are the creator)
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            # Associate the logged-in student with the submission
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

from ..models import Portion
from ..serializers import PortionSerializer

class PortionView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get_permissions(self):
        """
        Apply permissions for the view actions.
        """
        if self.request.method == 'GET':
            # Students and Faculty can retrieve portions
            return [IsAuthenticated(), (IsFaculty() | IsStudent())]
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Only Faculty can create, update, or delete portions
            return [IsAuthenticated(), IsFaculty()]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """
        Retrieve portions based on user role and optional filters:
        - Students can view portions for their standard and academic year.
        - Faculty can view all portions, optionally filtered by standard and academic year.
        """
        # Get query parameters for filtering
        standard = request.query_params.get('standard', None)
        academic_year = request.query_params.get('academic_year', None)

        # Base queryset
        queryset = Portion.objects.all()

        # Apply filters based on query parameters
        if standard:
            queryset = queryset.filter(standard=standard)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)

        # Additional restrictions for students
        if request.user.role == 'student':
            if not standard or not academic_year:
                return Response(
                    {'detail': 'Both standard and academic_year are required for students.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Serialize and return the data
        serializer = PortionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a new portion. Only faculty can create portions.
        """
        serializer = PortionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new portion
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, portion_id, *args, **kwargs):
        """
        Update an entire portion. Only faculty can update portions.
        """
        try:
            portion = Portion.objects.get(id=portion_id)
        except Portion.DoesNotExist:
            return Response({'detail': 'Portion not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PortionSerializer(portion, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated portion
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, portion_id, *args, **kwargs):
        """
        Partially update a portion. Only faculty can update portions.
        """
        try:
            portion = Portion.objects.get(id=portion_id)
        except Portion.DoesNotExist:
            return Response({'detail': 'Portion not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PortionSerializer(portion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the partially updated portion
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, portion_id, *args, **kwargs):
        """
        Delete a portion. Only faculty can delete portions.
        """
        try:
            portion = Portion.objects.get(id=portion_id)
        except Portion.DoesNotExist:
            return Response({'detail': 'Portion not found.'}, status=status.HTTP_404_NOT_FOUND)

        portion.delete()  # Delete the portion
        return Response({'detail': 'Portion deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

'''