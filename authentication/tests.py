# Django imports
from django.test import TestCase
from django.test.utils import mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

# Application imports
from .models import LoginToken
from .backends import EmailBackend


class TestRoutes(TestCase):
    """
    Tests the returned status codes of all routes for
    a logged in and an anonymous user.
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


class TestSignUpViews(TestCase):
    """
    Tests signup view.
    """
    def test_sign_up(self):
        """
        Tests a regular sign up.
        """
        response = self.client.post(
            reverse('signup'),
            {
                'email': 'test@zs.news',
                'first_name': 'Test',
                'last_name': 'Test'
            }
        )
        self.assertEquals(200, response.status_code)
        self.assertEquals(1, get_user_model().objects.count())
        self.assertEquals(1, LoginToken.objects.count())

    def test_invalid_email(self):
        """
        Tests signup if an invalid email address
        is given.
        """
        response = self.client.post(
            reverse('signup'),
            {
                'email': 'test@zs',
                'first_name': 'Test',
                'last_name': 'Test'
            }
        )
        self.assertEquals(200, response.status_code)
        self.assertEquals(0, get_user_model().objects.count())
        self.assertEquals(0, LoginToken.objects.count())


class TestLoginView(TestCase):
    """
    Tests login view. In particular if a login token is
    generated correctly.
    """
    def setUp(self):
        self.user = get_user_model().objects.create(email='test@zs.news')

    def tearDown(self):
        self.user.delete()

    def test_non_existent_user(self):
        """
        Tests that a non existent user cannot create
        a login token.
        """
        tokens_before = LoginToken.objects.count()
        self.client.post(reverse('login'), {'email': 'does_not_exist@zs.news'})
        self.assertEquals(tokens_before, LoginToken.objects.count())

    def test_inactive_user_token(self):
        """
        Tests that an inactive user cannot request
        a login token.
        """
        inactive_user = get_user_model().objects.create(email='test_inactive@zs.news', is_active=False)
        self.client.post(reverse('login'), {'email': inactive_user.email})
        self.assertEquals(0, LoginToken.objects.filter(user=inactive_user).count())

    def test_limit_of_requested_tokens(self):
        """
        Tests that the token limit is not exceeded.
        """
        for _ in range(settings.MAX_TOKEN_PER_USER):
            self.client.post(reverse('login'), {'email': self.user.email})
        self.assertEquals(settings.MAX_TOKEN_PER_USER, LoginToken.objects.filter(user=self.user).count())
        self.client.post(reverse('login'), {'email': self.user.email})
        self.assertEquals(settings.MAX_TOKEN_PER_USER, LoginToken.objects.filter(user=self.user).count())


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

    def test_valid_token(self):
        """
        Tests authentication with a valid token.
        """
        self.client.login(email=self.user.email, code=self.code)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.client.logout()
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_invalid_token(self):
        """
        Tests authentication with an invalid token. User should not be logged in.
        """
        self.client.login(email=self.user.email, code='invalid_token')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.client.login(email=self.user.email, code=None)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_inactive_login(self):
        """
        Tests that an inactive user can not login.
        """
        inactive_user = get_user_model().objects.create(email='test_inactive@zs.news', is_active=False)
        # Manually create token for inactive user
        code, token = LoginToken.objects.create(user=inactive_user)
        self.client.login(email=inactive_user.email, code=code)
        self.assertNotIn('_auth_user_id', self.client.session)
        inactive_user.delete()

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


class TestTokenView(TestCase):
    """
    Tests token verification route.
    """
    def setUp(self):
        self.user = get_user_model().objects.create(email='test@zs.news')
        self.code, self.token = LoginToken.objects.create(user=self.user)

    def tearDown(self):
        self.user.delete()

    def test_valid_credentials(self):
        """
        Tests login via URL with valid credentials.
        """
        response = self.client.get(reverse(
            'token_verification',
            kwargs={
                'email_b64': LoginToken.b64_encoded(self.user.email),
                'code': self.code
            }
        ))
        self.assertEqual(302, response.status_code)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_invalid_email(self):
        """
        Tests login via URL with an invalid email address.
        """
        response = self.client.get(reverse(
            'token_verification',
            kwargs={
                'email_b64': LoginToken.b64_encoded('invalid_user@zs.news'),
                'code': self.code
            }
        ))
        self.assertEqual(200, response.status_code)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_invalid_code(self):
        """
        Tests login via URL with an invalid code.
        """
        response = self.client.get(reverse(
            'token_verification',
            kwargs={
                'email_b64': LoginToken.b64_encoded(self.user.email),
                'code': 'invalid_code'
            }
        ))
        self.assertEqual(200, response.status_code)
        self.assertNotIn('_auth_user_id', self.client.session)
