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
        on_delete=models.CASCADE,
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
        'Bezahlt am',
        blank=True,
        null=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()

    class Meta:
        verbose_name = 'Zahlung'
        verbose_name_plural = 'Zahlungen'

    def __str__(self):
        return 'Payment({}, {}, {})'.format(self.subscription.user.email, self.amount, self.paid_at)

    def is_paid(self):
        return self.paid_at is not None
    is_paid.boolean = True

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
            subject='Rechnung',
            message=render_to_string('emails/invoice.txt', {
                'to_name': self.subscription.user.first_name,
                'payment': self
            }),
            from_email=None,
            recipient_list=[self.subscription.user.email],
            fail_silently=True
        )


    def confirm(self):
        """
        Confirms a payment by activating the subscription
        and sending a confirmation email.
        """
        # Confirm payment
        self.paid_at = timezone.now()
        self.save()

        # Fetch is_renewal value
        renewal = self.is_renewal()

        # Adjust subscription details
        if not renewal:
            self.subscription.start_date = timezone.now()
            self.subscription.end_date = timezone.now() + relativedelta(months=self.subscription.plan.duration)
            subject = 'Abo aktiviert'
        else:
            self.subscription.end_date += relativedelta(months=self.subscription.plan.duration)
            subject = 'Abo verlängert'
        self.subscription.save()

        # Send renewal confirmation email
        send_mail(
            subject=subject,
            message=('emails/payment_confirmation.txt', {
                'to_name': self.subscription.user.first_name,
                'payment': self,
                'renewal': renewal
            }),
            from_email=None,
            recipient_list=[self.subscription.user.email],
            fail_silently=True
        )
