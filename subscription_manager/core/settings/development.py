# Import base settings
from .base import *

BASE_URL = 'http://127.0.0.1:8000'
DEBUG = True

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
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
