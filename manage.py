#!/usr/bin/env python

import os
import sys

import dotenv

if __name__ == '__main__':
    # Load .env variables
    dotenv.read_dotenv()

    # Load settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscription_manager.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Couldn not import Django. Are you sure it is installed and '
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    execute_from_command_line(sys.argv)
