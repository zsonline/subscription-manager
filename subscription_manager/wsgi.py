import os

import dotenv

from django.core.wsgi import get_wsgi_application

# Load production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscription_manager.settings.production')

# Load .env variables
dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

application = get_wsgi_application()
