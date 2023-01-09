from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ User model, extends basic User model with some custom fields for Spotify. """
    accepted_account = models.BooleanField(default=False)
    spotify_access_token = models.CharField(max_length=400, default=None, blank=True, null=True)
    spotify_refresh_token = models.CharField(max_length=400, default=None, blank=True, null=True)
    spotify_token_expires_at = models.DateTimeField(default=None, blank=True, null=True)
    profile_picture = models.URLField(default=None, blank=True, null=True)

