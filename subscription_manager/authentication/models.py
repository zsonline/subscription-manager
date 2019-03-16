from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone

from .managers import TokenManager


class Token(models.Model):
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Abonnentin'
    )
    action = models.CharField(
        max_length=20,
        choices=(
            ('signup', 'Bestätigungs-Token'),
            ('login', 'Login-Token'),
            ('eligibility', 'Bestätigungs-Token')
        ),
        verbose_name='Typ'
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name='Code'
    )
    valid_until = models.DateTimeField(
        default=timezone.now() + settings.TOKEN_EXPIRATION,
        verbose_name='gültig bis'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='gesendet am'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TokenManager()

    class Meta:
        verbose_name = 'Token'

    def __str__(self):
        return 'Token({}, {})'.format(self.user.email, self.code)

    def is_valid(self):
        """
        True if the token is still valid.
        """
        return timezone.now() <= self.valid_until

    @staticmethod
    def url(code):
        """
        Returns the url for a given email address and code.
        Example: https://hostname.tld/auth/token/1836af19-67df-4090-8229-16ed13036480/
        """
        return '{}{}'.format(
            settings.BASE_URL,
            reverse(
                'token_verification',
                kwargs={
                    'code': code
                }
            )
        )

    def send(self, next_page=None):
        """
        Sends an email with the token code and updates
        sent_at field.
        """
        # Select template
        template = 'emails/' + self.action + '_token.txt'
        subject = self.get_action_display()

        # Generate url
        url = Token.url(self.code)
        if next_page is not None:
            url += '?next=' + next_page

        # Send email
        send_mail(
            subject=settings.EMAIL_SUBJECT_PREFIX + subject,
            message=render_to_string(template, {
                'to_name': self.user.first_name,
                'url': url,
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
            fail_silently=False
        )

        # Update sent_at field
        self.sent_at = timezone.now()
        self.save()
