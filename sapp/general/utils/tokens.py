# accounts/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from rest_framework_simplejwt.tokens import AccessToken

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Includes user-specific data to prevent token reuse
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)

email_verification_token = EmailVerificationTokenGenerator()

# New Custom Access Token class
class CustomAccessToken(AccessToken):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_role_to_payload()

    def add_role_to_payload(self):
        # Get the user profile (assuming you have a 'profile' related model like StudentDB or FacultyDB)
        user = self.user
        # Example: Check the user's profile role and add it to the payload
        role = user.profile.role if hasattr(user, 'profile') else 'student'  # Default to 'student' if no profile
        self.payload['role'] = role
