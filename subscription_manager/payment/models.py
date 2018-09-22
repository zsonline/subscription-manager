# Pip imports
from dateutil.relativedelta import relativedelta

# Django imports
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

# Project imports
from subscription_manager.subscription.models import Subscription

# Application imports
from .managers import PaymentManager


class Payment(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.DO_NOTHING,
        verbose_name='Abonnement'
    )
    amount = models.IntegerField(
        'Betrag'
    )
    code = models.CharField(
        max_length=30,
        unique=True
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()

    def __str__(self):
        return 'Payment({}, {}, {})'.format(self.subscription.user.email, self.amount, self.paid_at)

    def is_paid(self):
        return self.paid_at is not None

    def pay_until(self):
        return (self.created_at + relativedelta(days=30)).date()

    def is_renewal(self):
        return self.subscription.start_date is not None

    def send_invoice(self):
        """
        Sends an email that contains the payment details
        for this payment.
        """
        send_mail(
            '[ZS] Rechnung',
            render_to_string('emails/invoice.txt', {
                'to_name': self.subscription.user.first_name,
                'payment': self
            }),
            settings.ORGANISATION_FROM_EMAIL,
            [self.subscription.user.email],
            fail_silently=False
        )


    def confirm(self):
        """
        Confirms a payment by activating the subscription
        and sending a confirmation email.
        """
        # Confirm payment
        self.paid_at = timezone.now()
        self.save()

        # Adjust subscription details
        if self.subscription.start_date is None:
            self.subscription.start_date = timezone.now()
            self.subscription.end_date = timezone.now() + relativedelta(months=self.subscription.plan.duration)
            subject = 'Abo aktiviert'
        else:
            self.subscription.end_date += relativedelta(months=self.subscription.plan.duration)
            subject = 'Abo verlängert'
        self.subscription.save()

        # Send renewal confirmation email
        send_mail(
            '[ZS] ' + subject,
            render_to_string('emails/payment_confirmation.txt', {
                'to_name': self.subscription.user.first_name,
                'payment': self
            }),
            settings.ORGANISATION_FROM_EMAIL,
            [self.subscription.user.email],
            fail_silently=False
        )
