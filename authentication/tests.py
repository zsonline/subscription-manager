from django.test import TestCase, Client
from django.test.utils import mail
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.conf import settings

from .models import LoginToken
from .backends import EmailBackend


class TestRoutes(TestCase):
    """
    Tests whether all routes behave as they should.
    """
    def setUp(self):
        self.user = get_user_model().objects.create(email='test@zs.news')
        self.code, self.token = LoginToken.objects.create(user=self.user)

    def tearDown(self):
        self.user.delete()

    def test_anonymous(self):
        """
        Tests all routes for an anonymous visitor.
        """
        response = self.client.get(reverse('signup'))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('login'))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse(
            'token_verification',
            kwargs={
                'email_b64': 'cmVkYWt0aW9uQHpzLW9ubGluZS5jaA',
                'code': '1836af19-67df-4090-8229-16ed13036480'
            }
        ))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('logout'))
        self.assertEqual(302, response.status_code)

    def test_logged_in(self):
        """
        Tests all routes for a logged in user.
        """
        self.client.login(email=self.user.email, code=self.code)

        response = self.client.get(reverse('signup'))
        self.assertEqual(302, response.status_code)

        response = self.client.get(reverse('login'))
        self.assertEqual(302, response.status_code)

        response = self.client.get(reverse(
            'token_verification',
            kwargs={
                'email_b64': 'cmVkYWt0aW9uQHpzLW9ubGluZS5jaA',
                'code': '1836af19-67df-4090-8229-16ed13036480'
            }
        ))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('logout'))
        self.assertEqual(302, response.status_code)


class TestLogin(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(email='test@zs.news')
        self.code, self.token = LoginToken.objects.create(user=self.user)
        self.inactive_user = get_user_model().objects.create(email='test_inactive@zs.news', is_active=False)

    def test_url_authentication(self):
        client = Client()
        response = client.get(reverse(
            'token_verification',
            kwargs={
                'email_b64': LoginToken.b64_encoded(self.user.email),
                'code': self.code
            }
        ))
        self.assertEqual(302, response.status_code)
        response = client.get(settings.LOGIN_REDIRECT_URL)
        print('hi\n\n')
        print(response)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_inactive(self):
        self.assertEqual(0, LoginToken.objects.filter(user=self.inactive_user).count())
        self.assertEqual(None, LoginToken.objects.create(user=self.inactive_user))


class TestBackends(TestCase):
    """
    Tests the custom authentication backends for
    token authentication.
    """
    def setUp(self):
        self.user = get_user_model().objects.create(email='test@zs.news')
        self.code, self.token = LoginToken.objects.create(user=self.user)

    def tearDown(self):
        self.user.delete()

    def test_email_backend(self):
        """
        Tests the email backend, in particular whether
        the email contains the correct login url.
        """
        mail.outbox = []
        EmailBackend.send(self.token, self.code)
        self.assertEqual(1, len(mail.outbox))
        message = mail.outbox[0]
        self.assertIn(LoginToken.login_url(self.user.email, self.code), message.body)
        self.assertEqual([self.user.email], message.to)
