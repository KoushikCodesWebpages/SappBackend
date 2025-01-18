from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes  # Use smart_bytes instead of force_bytes
from django.contrib.sites.shortcuts import get_current_site
from .tokens import email_verification_token  # Import your token generator

def send_verification_email(user, request):
    # Generate the verification token and encoded user ID
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(smart_bytes(user.pk))  # Use smart_bytes here

    # Build the verification link
    current_site = get_current_site(request)
    verify_url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    verification_link = f"http://{current_site.domain}{verify_url}"

    # Send the email
    send_mail(
        'Verify Your Email Address',
        f'Hi {user.username},\nPlease click the link to verify your email:\n{verification_link}',
        'CharityHubForDemo@gmail.com',  # Replace with your email
        [user.email],   
        fail_silently=False,
    )
