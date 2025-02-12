from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from datetime import date
from accounts.models import Student
from features.models import Attendance,AttendanceLock

from features.serializers import AttendanceLockSerializer, AttendanceSerializer

from general.utils.permissions import IsFaculty,IsOfficeAdmin, IsStudent


class AttendanceLockView(APIView):
    def get_permissions(self):
        """Dynamically assign permissions based on request method."""
        if self.request.method == "GET":
            return [IsAuthenticated(), permissions.OR(IsFaculty(), IsOfficeAdmin())]  # Faculty and Office Admin can GET
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsOfficeAdmin()]  # Only Office Admin can POST, PUT, PATCH, DELETE
        return [IsAuthenticated()]  # Default case (shouldn't happen)

    def get(self, request):
        """
        GET: Return the latest AttendanceLock for the current date.
        Allowed for faculty and office roles only.
        """
        today = date.today()
        try:
            attendance_lock = AttendanceLock.objects.filter(date=today).latest('id')
            serializer = AttendanceLockSerializer(attendance_lock)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AttendanceLock.DoesNotExist:
            return Response({"detail": "Wait till permission for attendance is given for today."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        POST: Create a new AttendanceLock entry for a specific date.
        Allowed for office role only.
        """
        date_to_lock = request.data.get('date')
        if AttendanceLock.objects.filter(date=date_to_lock).exists():
            return Response({"detail": "Attendance lock for this date already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AttendanceLockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        PUT: Update the 'is_locked' field of an existing AttendanceLock.
        Allowed for office role only, and only when 'is_locked' is currently false.
        """
        return self.partial_update(request)

    def patch(self, request):
        """
        PATCH: Partially update an existing AttendanceLock.
        Allowed for office role only.
        """
        return self.partial_update(request)

    def partial_update(self, request):
        """Helper method for PUT and PATCH."""
        date_to_update = request.data.get('date')
        try:
            attendance_lock = AttendanceLock.objects.get(date=date_to_update)

            serializer = AttendanceLockSerializer(attendance_lock, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AttendanceLock.DoesNotExist:
            return Response({"detail": "Attendance lock for this date does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """
        DELETE: Remove an AttendanceLock entry.
        Allowed for office role only.
        """
        date_to_delete = request.data.get('date')
        try:
            attendance_lock = AttendanceLock.objects.get(date=date_to_delete)
            attendance_lock.delete()
            return Response({"detail": "Attendance lock deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except AttendanceLock.DoesNotExist:
            return Response({"detail": "Attendance lock for this date does not exist."}, status=status.HTTP_404_NOT_FOUND)
        

class AttendanceDaysView(APIView):
    def get_permissions(self):
        """Dynamically assign permissions based on request method."""
        return [IsAuthenticated(), permissions.OR(IsFaculty(), IsOfficeAdmin())]  # Only Faculty & Office Admin can access

    def get(self, request):
        """
        GET: Retrieve all locked (working days) and unlocked (non-working days) dates.
        Allowed for faculty and office roles only.
        """
        # Check permissions explicitly and return error if access is denied
        if not any(permission.has_permission(request, self) for permission in self.get_permissions()):
            return Response({"detail": "Access denied. You do not have permission to view attendance days."}, 
                            status=status.HTTP_403_FORBIDDEN)

        locked_days = AttendanceLock.objects.filter(is_locked=True).values_list('date', flat=True)
        unlocked_days = AttendanceLock.objects.filter(is_locked=False).values_list('date', flat=True)

        return Response({
            "working_days": list(locked_days),
            "non_working_days": list(unlocked_days)
        }, status=status.HTTP_200_OK)
    
    

class AttendanceView(APIView):
    def get_permissions(self):
        """Dynamically assign permissions based on request method."""
        if self.request.method == "POST" or self.request.method == "PUT":
            return [IsAuthenticated(), IsFaculty()]  # Only Faculty can create/update
        elif self.request.method == "GET":
            return [IsAuthenticated(), permissions.OR(IsFaculty(), IsStudent())]  # Faculty & Students can view
        return [IsAuthenticated()]  # Default case (shouldn't happen)

    def post(self, request, *args, **kwargs):
        """
        Post attendance for multiple students. Only faculty members can create attendance records.
        """
        # Check permissions explicitly and return error if access is denied
        if not all(permission.has_permission(request, self) for permission in self.get_permissions()):
            return Response({"detail": "Access denied. You do not have permission to create attendance records."}, 
                            status=status.HTTP_403_FORBIDDEN)

        if isinstance(request.data, list):
            attendance_objects = []

            for record in request.data:
                student_code = record.get("student")
                date = record.get("date")
                status_value = record.get("status")

                try:
                    student = Student.objects.get(student_code=student_code)
                except Student.DoesNotExist:
                    return Response({"detail": f"Student with student_code {student_code} does not exist."}, 
                                     status=status.HTTP_400_BAD_REQUEST)

                attendance = Attendance(student=student, date=date, status=status_value)
                attendance_objects.append(attendance)

            Attendance.objects.bulk_create(attendance_objects)

            return Response({"message": "Attendance records created successfully"}, status=status.HTTP_201_CREATED)

        return Response({"detail": "Invalid data format. Expected a list of attendance records."}, 
                        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Get attendance based on student standard and section, or by authenticated user's email.
        """
        # Check permissions
        if not any(permission.has_permission(request, self) for permission in self.get_permissions()):
            return Response({"detail": "Access denied. You do not have permission to view attendance records."}, 
                            status=status.HTTP_403_FORBIDDEN)

        email = request.query_params.get("email")
        standard = request.query_params.get("standard")
        section = request.query_params.get("section")
        academic_year = request.query_params.get("academic_year")

        if email:
            if email != request.user.email:
                return Response({"detail": "You are not authorized to access this student's attendance."}, 
                                status=status.HTTP_403_FORBIDDEN)

            attendance = Attendance.objects.filter(student__student_code__startswith=email)
        elif standard and section and academic_year:
            attendance = Attendance.objects.filter(student__student_code__endswith=f"-{standard}-{section}-{academic_year}")
        else:
            attendance = Attendance.objects.all()

        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        Update attendance for multiple students. Only faculty members can update attendance records.
        """
        if not all(permission.has_permission(request, self) for permission in self.get_permissions()):
            return Response({"detail": "Access denied. You do not have permission to update attendance records."}, 
                            status=status.HTTP_403_FORBIDDEN)

        if isinstance(request.data, list):
            updated_data = []
            for record in request.data:
                student_code = record.get("student_code")
                date = record.get("date")
                status = record.get("status")

                try:
                    student = Student.objects.get(student_code=student_code)
                except Student.DoesNotExist:
                    return Response({"detail": f"Student with student_code {student_code} does not exist."}, 
                                    status=status.HTTP_400_BAD_REQUEST)

                attendance = Attendance.objects.filter(student=student, date=date).first()
                if attendance:
                    attendance.status = status
                    attendance.save()
                    updated_data.append(AttendanceSerializer(attendance).data)
                else:
                    attendance_data = {"student": student.id, "date": date, "status": status}
                    serializer = AttendanceSerializer(data=attendance_data)
                    if serializer.is_valid():
                        serializer.save()
                        updated_data.append(serializer.data)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(updated_data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid data format. Expected a list of attendance records."}, 
                        status=status.HTTP_400_BAD_REQUEST)
