from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from urllib.parse import urlparse

from users.storage_backends import MediaStorage


class User(AbstractUser):
    image = models.ImageField(
        upload_to='users_image/',
        storage=MediaStorage() if MediaStorage else None,
        null=True,
        blank=True
    )
    is_verified_email = models.BooleanField(default=False)

    @property
    def image_path(self):
        return urlparse(self.image.url).path

    def __str__(self):
        return self.username


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'Email Verification object for {self.user.email}'

    def send_verification_email(self):
        link = reverse('users:email_verification', kwargs={'email': self.user.email, 'code': self.code})
        verification_link = f'{settings.DOMAIN_NAME}{link}'
        subject = f'Verifying account for {self.user.username}'
        message = 'For verifying email for {} follow the link: {}'.format(
            self.user.email,
            verification_link
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return True if now() >= self.expiration else False
