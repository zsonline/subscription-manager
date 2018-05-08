# Python imports
import os

# Pip imports
from dotenv import load_dotenv

# Django imports
from django.core.wsgi import get_wsgi_application

# Load .env file
load_dotenv()
# Load production settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")

# https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
application = get_wsgi_application()
