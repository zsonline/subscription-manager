"""
WSGI config for zsavs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

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

application = get_wsgi_application()
