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


 # Adjust the import based on your project structure
 # Adjust the import based on your project structure

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



