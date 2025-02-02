from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from general.utils.permissions import IsFaculty
from features.models import Assignment, Submission
from features.serializers import AssignmentSerializer, AssignmentMinSerializer, SubmissionSerializer, SubmissionMinSerializer
from general.utils.permissions import IsFaculty, IsStudent



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
 