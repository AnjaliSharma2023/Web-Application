from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


# extend the PasswordResetTokenGenerator to create a unique token generator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.userprofile.signup_confirmation)
        )

account_activation_token = AccountActivationTokenGenerator()