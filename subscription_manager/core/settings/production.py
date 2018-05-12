# Import base settings
from .base import *

# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ALLOWED_HOSTS = []

SECURE_SSL_REDIRECT = True

WSGI_APPLICATION = 'subscription_manager.wsgi.application'
