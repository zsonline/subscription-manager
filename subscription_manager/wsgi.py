# Python imports
import os

# Django imports
from django.core.wsgi import get_wsgi_application

# Load production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscription_manager.settings.production')

application = get_wsgi_application()
