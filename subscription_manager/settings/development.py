# Import base settings
from .base import *

BASE_URL = 'http://localhost:8000'
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
INTERNAL_IPS = ['127.0.0.1']

# Secret key (default value is set in development
# settings so that the .env file is not necessary)
SECRET_KEY = 'fruh-%ut#q*2av0@d+vf!*gkc=vbnxwox^h6-a-$9avh32z+ya'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'db.sqlite3'),
    }
}

# Email
EMAIL_BACKEND = 'post_office.EmailBackend'
POST_OFFICE = {
    'BACKENDS': {
        'default': 'django.core.mail.backends.console.EmailBackend'
    }
}

COMPRESS_ENABLED = False
