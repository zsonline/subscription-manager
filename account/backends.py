from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode

from .models import Token, User


class TokenBackend(object):
    def authenticate(self, user_id=None, key=None):
        try:
            token = Token.objects.get(key=key)
            if token.is_valid():
                user = token.user
                if user.id == user_id:
                    token.delete()
                    if user.is_active:
                        return user
            return None
        except Token.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
