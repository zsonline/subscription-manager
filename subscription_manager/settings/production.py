# Import base settings
from .base import *

# General
DEBUG = False
ALLOWED_HOSTS = ['abo.zs-online.ch', 'www.abo.zs-online.ch']
BASE_URL = 'https://www.abo.zs-online.ch'  # Used for sending email links

# Security
SECRET_KEY = env('SECRET_KEY')
CSRF_COOKIE_SECURE = True

# Server
WSGI_APPLICATION = 'subscription_manager.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    }
}
CONN_MAX_AGE = None

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_SECURE = True

# Email
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = env('EMAIL_USE_SSL')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/subscription-manager/django.log'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
