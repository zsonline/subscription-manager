import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscription_manager.settings.production')

application = get_wsgi_application()

try:
    from uwsgidecorators import cron, timer

    from django.core.management import call_command

    from subscription_manager.user.models import Token

    @timer(5)
    def send_queued_mail(signum):
        """
        Send queued mail every 5 seconds
        """
        call_command('send_queued_mail', '--processes=1', '--verbosity=0')

    @cron(0, 4, -1, -1, -1)
    def clean_database(num):
        """
        Clear expired sessions, remove expired tokens
        and clean email log each day at 4 am.
        """
        call_command('clearsessions', '--verbosity=0')
        Token.objects.all_expired().delete()
        call_command('cleanup_mail', '--days=30', '--delete-attachments', '--verbosity=0')

except ImportError:
    print("uwsgidecorators not found. Cron and timers are disabled")