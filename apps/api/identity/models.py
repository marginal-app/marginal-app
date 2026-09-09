from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class ApiToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_token",
    )
    key_hash = models.CharField(max_length=64, unique=True)
    hint = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
