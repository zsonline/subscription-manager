# Python imports
import os
from datetime import timedelta


# Organisation
ORGANISATION_NAME = 'Zürcher Studierendenzeitung'
ORGANISATION_ABBREVIATION = 'ZS'
ORGANISATION_REPLY_TO_EMAIL = 'support@zs-online.ch'
ORGANISATION_FROM_EMAIL = 'server@zs-online.ch'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'subscription_manager.authentication.apps.AccountConfig',
    'subscription_manager.payment.apps.PaymentConfig',
    'subscription_manager.subscription.apps.SubscriptionConfig',
    'subscription_manager.user.apps.UserConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'subscription_manager.core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'subscription_manager.utils.context_processors.setting_variables'
            ],
            'libraries': {
                'navigation': 'subscription_manager.utils.templatetags.navigation',
            },
        },
    },
]

# Specifies custom user model
AUTH_USER_MODEL = 'user.User'
# Authentication backends
AUTHENTICATION_BACKENDS = [
    'subscription_manager.authentication.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend'
]

# Login tokens
TOKENS_PER_USER = 3  # Maximum amount of tokens per user
TOKEN_EXPIRATION = timedelta(minutes=10)  # Validity duration of a token

ALLOWED_STUDENT_EMAIL_ADDRESSES = ['student.ethz.ch']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Fixed auth urls
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/home/'

# Internationalization
LANGUAGE_CODE = 'de'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
