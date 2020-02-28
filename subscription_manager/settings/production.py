# Import base settings
from .base import *

# General
DEBUG = False
ALLOWED_HOSTS = ['abo.zs-online.ch', 'www.abo.zs-online.ch']
BASE_URL = 'https://www.abo.zs-online.ch'  # Used for sending email links

# Security
SECRET_KEY = os.environ['SECRET_KEY']
CSRF_COOKIE_SECURE = True

# Server
WSGI_APPLICATION = 'subscription_manager.wsgi.application'

# Database
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

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_SECURE = True

# Email
EMAIL_USE_SSL = True
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log'
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
