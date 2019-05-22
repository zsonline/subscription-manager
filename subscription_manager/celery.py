import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscription_manager.settings.production')

app = Celery('subscription_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.timezone = 'Europe/Zurich'

app.conf.beat_schedule = {
    # Executes everyday at 6am.
    'send-expiration-emails': {
        'task': 'tasks.add',
        'schedule': crontab(minute=0, hour=6),
    },
}


@app.task(name='send-expiration-emails')
def send_expiration_emails():
    """
    Sends expiration emails to users.
    """
    from subscription_manager.subscription.models import Subscription
    Subscription.objects.send_expiration_emails()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
