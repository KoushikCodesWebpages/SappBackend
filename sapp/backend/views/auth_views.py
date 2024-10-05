from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from backend.serializers.auth_serializers import SignUpSerializer, LoginSerializer
from backend.utils.tokens import email_verification_token
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from backend.serializers.auth_serializers import PasswordResetRequestSerializer,SetNewPasswordSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import authenticate
from backend.models.user_models import StudentsDB, FacultyDB,  Section, Standard

# views.py


from rest_framework.permissions import AllowAny
# views.py
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)

            # Generate token and UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create password reset link
            current_site = get_current_site(request)
            reset_url = reverse('reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_link = f"http://{current_site.domain}{reset_url}"

            # Send email
            send_mail(
                'Password Reset Request',
                f'Hi {user.username},\nPlease click the link to reset your password:\n{reset_link}',
                'koushikaltacc',  # Replace with your email
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        try:
            # Decode the uid and retrieve the user
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)

            # Check if the token is valid
            if email_verification_token.check_token(user, token):
                user.is_active = True  # Activate the user account
                user.save()
                
                # Inline HTML response for success
                return HttpResponse('''
                    <html>
                        <head><title>Email Verification</title></head>
                        <body>
                            <h1>Email Verified Successfully</h1>
                            <p>Your email has been verified. You can now log in to your account.</p>
                        </body>
                    </html>
                ''')
            else:
                # Inline HTML response for failure
                return HttpResponse('''
                    <html>
                        <head><title>Email Verification Failed</title></head>
                        <body>
                            <h1>Email Verification Failed</h1>
                            <p>The verification link is invalid or has expired.</p>
                        </body>
                    </html>
                ''', status=400)
        except Exception:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            # Create user
            user = serializer.save()
            user.is_active = False  # Deactivate account until email verification
            user.save()

            # Generate the verification token and encoded user ID
            token = email_verification_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build the verification link
            current_site = get_current_site(request)
            verify_url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            verification_link = f"http://{current_site.domain}{verify_url}"

            # Send email
            send_mail(
                'Verify Your Email Address',
                f'Hi {user.username},\nPlease click the link to verify your email:\n{verification_link}',
                'CharityHubForDemo@gmail.com',  # Replace with your email
                [user.email],
                fail_silently=False,
            )

            # Based on role, create student or faculty profile
            role = request.data.get('role')  # Get role from the request
            if role == 'student':
                standard_id = request.data.get('standard')  # Get standard ID from the request
                section_id = request.data.get('section')  # Get section ID from the request
                standard = Standard.objects.get(id=standard_id)
                section = Section.objects.get(id=section_id)
                # Create a student profile
                StudentsDB.objects.create(user=user, standard=standard, section=section)

            elif role == 'faculty':
                section_id = request.data.get('section')  # Get section ID from the request (optional)
                section = Section.objects.get(id=section_id) if section_id else None
                # Create a faculty profile
                FacultyDB.objects.create(
                    user=user,
                    name=request.data.get('name'),
                    address=request.data.get('address'),
                    reg_no=request.data.get('reg_no'),
                    role=request.data.get('role'),
                    section=section
                )

            return Response({'message': 'Verification email sent'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# accounts/views.py

from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Extracting email and password from the request body
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if both email and password are provided
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the password is correct
        if user.check_password(password):
            if user.is_active:
                # User is authenticated and active, generate tokens
                access_token = AccessToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)

                # Determine if the user is a student or faculty
                role = 'student' if StudentsDB.objects.filter(user=user).exists() else 'faculty' if FacultyDB.objects.filter(user=user).exists() else None

                if role is None:
                    return Response({'error': 'User has no associated role'}, status=status.HTTP_400_BAD_REQUEST)

                # Return tokens and role
                return Response({
                    'access': str(access_token),
                    'refresh': str(refresh_token),
                    'role': role,
                }, status=status.HTTP_200_OK)
            else:
                # User is not active (email not verified)
                return Response({'error': 'Email not verified'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # Invalid password
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
     
        
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)

            # Blacklist the refresh token
            token.blacklist()

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
