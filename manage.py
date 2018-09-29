#!/usr/bin/env python

# Python imports
import os
import sys

if __name__ == '__main__':
    # Load settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscription_manager.core.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Couldn not import Django. Are you sure it is installed and '
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    execute_from_command_line(sys.argv)
