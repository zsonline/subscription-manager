from django.contrib.auth import backends

from .models import Token


class TokenBackend(backends.ModelBackend):
    """
    Custom authentication backend that handles
    authentication by token.
    """
    def authenticate(self, request, code=None, **kwargs):
        """
        Checks if a given token is valid. If so, the user is returned,
        otherwise None.
        """
        # If code is None, authentication fails
        if code is None:
            return None

        # Encode code and find it in database
        token = Token.objects.get(code=code)
        # If token is valid, delete token and return user
        if token is not None and token.is_valid():
            user = token.email_address.user
            token.delete()
            if user.is_active:
                return user

        return None
