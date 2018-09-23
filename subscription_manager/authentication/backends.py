# Django imports
from django.contrib.auth import backends
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.template.loader import render_to_string

# Application imports
from .models import Token


class TokenBackend(backends.ModelBackend):
    """
    Custom authentication backend that handles authentication
    by token.
    """
    def authenticate(self, request, email=None, code=None, **kwargs):
        """
        Checks if a given token is valid for a given email
        address. If so, the user is returned, otherwise None.
        """
        # If email or code are None, authentication failed.
        if email is None or code is None:
            return None

        # Encode code and find it in database
        token = Token.objects.get_from_code(code)
        # If token is valid, delete token and return user
        if token is not None and token.is_valid():
            user = token.user
            if user.email == email:
                token.delete()
                if user.is_active:
                    return user
        return None


class EmailBackend(TokenBackend):
    """
    Inherits LoginTokenBackend class and adds
    a send method that sends tokens via email.
    """
    @staticmethod
    def send(token, code, action, next_page):
        """
        Creates and sends a token email for a
        given token object and a code.
        """
        # Select template
        template = 'emails/login_token.txt'
        subject = 'Login Token'
        if action == 'signup':
            template = 'emails/signup_token.txt'
            subject = 'Account bestätigen'

        # Generate url
        url = Token.url(token.user.email, code)
        if next_page is not None:
            url += '?next=' + next_page

        # Send email
        send_mail(
            '[ZS] ' + subject,
            render_to_string(template, {
                'to_name': token.user.first_name,
                'url': url,
            }),
            settings.ORGANISATION_FROM_EMAIL,
            [token.user.email],
            fail_silently=False
        )
