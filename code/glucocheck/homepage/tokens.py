from django.contrib.auth.tokens import PasswordResetTokenGenerator
try:
    from django.utils import six
except ImportError:
    import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    '''Creates a token related to the user used for account activation and password resetting.'''
    
    @staticmethod
    def _make_hash_value(user, timestamp):
        '''Returns a hash value specific to the user_id, is_active value, and the time of creation.
    
        Keyword arguments:
        user -- the user object
        timestamp -- the time of the token creation
        '''
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()