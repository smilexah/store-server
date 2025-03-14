from datetime import timedelta
from http import HTTPStatus

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from users.models import EmailVerification, User


class UserRegistrationViewTestCase(TestCase):
    def setUp(self):
        self.path = reverse('users:registration')

        self.data = {
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }

        social_app = SocialApp.objects.create(
            provider='github',
            name='Test GitHub App',
            client_id='test_client_id',
            secret='test_secret_key'
        )
        social_app.sites.add(Site.objects.get_current())

    def test_user_registration_get(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store | Registration')
        # self.assertEqual(response.context_data['form'], UserRegistrationForm())
        self.assertTemplateUsed(response, 'users/registration.html')

    def test_user_registration_post_success(self):
        username = self.data['username']
        self.assertFalse(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=username).exists())

        # check creating of email verification object
        email_verification = EmailVerification.objects.filter(user__username=username)
        self.assertTrue(email_verification.exists())
        self.assertEqual(
            email_verification.first().expiration.date(),
            (now() + timedelta(hours=1)).date()
        )

    def test_user_registration_post_error(self):
        User.objects.create(username=self.data['username'])
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пользователь с таким именем уже существует.', html=True)
