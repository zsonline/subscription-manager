# Import base settings
from .base import *

"""
Check before deploying:
https://docs.djangoproject.com/en/dev/howto/deployment/checklist/
"""

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False
ALLOWED_HOSTS = ['abo.zs-online.ch', 'www.abo.zs-online.ch', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT']
    }
}
CONN_MAX_AGE = None

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']

WSGI_APPLICATION = 'subscription_manager.core.wsgi.application'

STATIC_ROOT = "/srv/http/static/"

# TODO: Logging
# TODO: Cached template loader

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
