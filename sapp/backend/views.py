from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, StudentsDBSerializer, FacultyDBSerializer
from .models import StudentsDB, FacultyDB
from .pagination import CustomPagination
from .utils import BaseDBView

class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials or new user, please sign up.'}, status=status.HTTP_400_BAD_REQUEST)


class StudentsProfileView(BaseDBView):
    model_class = StudentsDB
    serializer_class = StudentsDBSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view
    pagination_class = CustomPagination


class FacultyProfileView(BaseDBView):
    model_class = FacultyDB
    serializer_class = FacultyDBSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view
    pagination_class = CustomPagination
