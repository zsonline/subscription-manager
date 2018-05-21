# Django imports
from django.contrib.auth import backends
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
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
    def send(token, code):
        """
        Creates and sends a login token email for a
        given token object and a code. It makes a .txt
        and a .html version of the email.
        """
        # Make a context variable for the templates
        context = {
            'to_name': token.user.first_name,
            'from_name': settings.ORGANISATION_NAME,
            'url': Token.url(token.user.email, code),
        }
        # Render the content templates
        text_content = render_to_string('authentication/emails/login_token.txt', context)
        html_content = render_to_string('authentication/emails/login_token.html', context)
        # Create the text and html version of the email
        message = EmailMultiAlternatives(
            subject='Token',
            body=text_content,
            from_email=settings.ORGANISATION_FROM_EMAIL,
            to=[token.user.email],
            headers={
                'Reply-To': settings.ORGANISATION_REPLY_TO_EMAIL
            }
        )
        message.attach_alternative(html_content, 'text/html')
        # Send the email
        message.send()
