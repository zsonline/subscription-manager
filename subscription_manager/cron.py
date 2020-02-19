from django_cron import CronJobBase, Schedule

from django.core.management import call_command

from subscription_manager.subscription.models import Subscription
from subscription_manager.user.models import Token


class SendEmails(CronJobBase):
    schedule = Schedule(run_at_times=['07:00'])
    code = 'send_emails'

    def do(self):
        """
        Send notification emails to users whose subscriptions are
        expiring within 30 days or whose subscription end in 1 day.
        """
        Subscription.objects.send_expiration_emails(30)
        Subscription.objects.send_expiration_emails(1)


class CleanDatabase(CronJobBase):
    schedule = Schedule(run_at_times=['04:00'])
    code = 'clean_database'

    def do(self):
        """
        Clear expired sessions and remove expired tokens
        each day at 4 am.
        """
        call_command('clearsessions', '--verbosity=0')
        Token.objects.all_expired().delete()