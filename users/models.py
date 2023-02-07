from djongo import models
from django.contrib.auth.models import AbstractUser
from encrypted_model_fields.fields import EncryptedCharField


class Profile(AbstractUser):
    email = models.EmailField(blank=False, max_length=254, verbose_name="email address")
    bio = models.TextField(blank=True, null=True)
    google_api_key = EncryptedCharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = "username"  # e.g: "username", "email"
    EMAIL_FIELD = "email"  # e.g: "email", "primary_email"
