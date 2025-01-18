from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from rest_framework import status

from django.contrib.auth import authenticate
from .serializers import StudentSignupSerializer, FacultySignupSerializer, StudentLoginSerializer, FacultyLoginSerializer

from general.utils.send_mail import send_verification_email

from general.utils.tokens import email_verification_token



User = get_user_model()

class StudentSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Perform custom validation
        username = request.data.get('username')
        email = request.data.get('email')
        roll_number = request.data.get('roll_number')

        # Validate email format and uniqueness
        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        

        # Now validate the data using the serializer
        serializer = StudentSignupSerializer(data=request.data)
        if serializer.is_valid():
            # Create the user and student profile
            user = serializer.create(validated_data=serializer.validated_data)

            # Send verification email
            #send_verification_email(user, request)

            return Response({
                "message": "Student signed up successfully. Please check your email for verification.",
            }, status=status.HTTP_201_CREATED)

        # Return any validation errors from the serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Authenticate user
            user = authenticate(username=username, password=password)
            if user is not None:
                # If user is authenticated, create tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class FacultySignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FacultySignupSerializer(data=request.data)
        if serializer.is_valid():
            # Create the user and faculty profile
            faculty = serializer.save()

            # Deactivate account until email verification
            faculty.user.is_active = False
            faculty.user.save()

            # Send the verification email using the utility function
            #send_verification_email(faculty.user, request)

            return Response({
                "message": "Faculty signed up successfully. Verification email sent.",
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FacultyLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FacultyLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Authenticate user
            user = authenticate(username=username, password=password)
            if user is not None:
                # If user is authenticated, create tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


