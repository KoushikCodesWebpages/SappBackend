from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from backend.serializers.auth_serializers import SignUpSerializer, LoginSerializer
from backend.utils.tokens import email_verification_token


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.serializers.auth_serializers import PasswordResetRequestSerializer,SetNewPasswordSerializer
from backend.utils.tokens import email_verification_token
from django.contrib.auth import get_user_model


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
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
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

            return Response({'message': 'Verification email sent'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# accounts/views.py

class LoginView(APIView):
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
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        # Check the password directly
        if user.check_password(password):
            if user.is_active:
                # User is authenticated and active
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                # User is not active (not verified)
                return Response({'error': 'Email not verified'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # Authentication failed
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)



