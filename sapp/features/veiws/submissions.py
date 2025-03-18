from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from features.models import Submission,Assignment
from features.serializers import SubmissionSerializer
from general.utils.permissions import IsFaculty, IsStudent
from accounts.models import Student


class StudentSubmissionViewSet(viewsets.ModelViewSet):
    """API for students to manage their own submissions."""
    
    permission_classes = [IsAuthenticated, IsStudent]
    pagination_class = None
    lookup_field = "id"
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        """
        Students can only view, update, or delete their own submissions.
        """
        student = getattr(self.request.user, "student_profile", None)  # ✅ Ensure we get the correct Student instance
        if not student:
            return Submission.objects.none()  # ✅ Return empty queryset if the user is not a student
        
        return Submission.objects.filter(student=student)

    def list(self, request, *args, **kwargs):
        """Filter submissions by assignment ID."""
        assignment = request.query_params.get("assignment")
        queryset = self.get_queryset().filter(assignment=assignment) if assignment else self.get_queryset()
        return Response(self.get_serializer(queryset, many=True).data or {"detail": "No submissions found."}, 
                        status=status.HTTP_200_OK if queryset else status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """
        Allow students to create submissions but prevent them from setting marks.
        """
        data = request.data.copy()
        
        # Get the student instance from the logged-in user
        student = request.user.student_profile  # ✅ Ensure we use the correct Student instance
        data["student"] = student.pk  # ✅ Assign the correct primary key (student_code)
        
        # Prevent students from submitting a mark
        data.pop("mark", None)  # ✅ Remove mark if it exists

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=student)  # ✅ Save with the Student instance

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Restrict students from modifying assignment, student, or mark fields."""
        if any(field in request.data for field in {"assignment", "student", "mark"}):
            return Response({"detail": "You cannot modify assignment, student, or marks."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

class FacultySubmissionViewSet(viewsets.ModelViewSet):
    """API for faculty to view all submissions for a specific assignment."""

    permission_classes = [IsAuthenticated, IsFaculty]
    pagination_class = None
    serializer_class = SubmissionSerializer
    lookup_field = "id"
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        """
        Faculty can view:
        - All submissions for a given assignment (when `assignment` query param is provided).
        - A single submission (when `id` is provided in the URL).
        """
        assignment_id = self.request.query_params.get("assignment")
        submission_id = self.kwargs.get("id")  # ✅ Fetch submission ID from URL

        if submission_id:  # ✅ If fetching a single submission by ID
            return Submission.objects.filter(id=submission_id)

        if assignment_id:  # ✅ If fetching all submissions for an assignment
            return Submission.objects.filter(assignment_id=assignment_id)

        return Submission.objects.none()  # ✅ Prevent unauthorized access


    def retrieve(self, request, *args, **kwargs):
        """Get a single submission by ID."""
        submission = get_object_or_404(Submission, id=kwargs["id"])
        serializer = self.get_serializer(submission)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """Return submissions along with student submission stats."""
        assignment_id = request.query_params.get("assignment")
        if not assignment_id:
            return Response({"detail": "Assignment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        submissions = self.get_queryset()
        submitted_students_count = submissions.count()  # ✅ Get total submitted count

        assignment = get_object_or_404(Assignment, id=assignment_id)
        total_students = Student.objects.filter(
            standard=assignment.standard,
            section=assignment.section,
            academic_year=assignment.academic_year
        )
        not_submitted_students = total_students.exclude(student_code__in=submissions.values_list("student__student_code", flat=True))

        return Response({
            "total_students": total_students.count(),
            "submitted_students_count": submitted_students_count,
            "not_submitted_students": [
                {"name": s.user.username, "student_code": s.student_code} for s in not_submitted_students
            ],
            "submissions": self.get_serializer(submissions, many=True).data
        })


    def update(self, request, *args, **kwargs):
            """
            Allow faculty to update only the `mark` field.
            """
            instance = self.get_object()

            if "mark" not in request.data:
                return Response(
                    {"detail": "You can only update marks."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)
