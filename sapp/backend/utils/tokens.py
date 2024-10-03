# accounts/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Includes user-specific data to prevent token reuse
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)

email_verification_token = EmailVerificationTokenGenerator()
