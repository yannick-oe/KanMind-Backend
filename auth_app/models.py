"""Data structures for the authentication application."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager

FULLNAME_MAX_LENGTH = 150


class User(AbstractUser):
    """User identified by a unique email and a single fullname field."""

    username = None
    first_name = None
    last_name = None

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=FULLNAME_MAX_LENGTH)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["id"]

    def __str__(self) -> str:
        """Return the user's fullname as its representation."""
        return self.fullname

    def get_full_name(self) -> str:
        """Return the fullname (replaces the removed name fields)."""
        return self.fullname

    def get_short_name(self) -> str:
        """Return the fullname (replaces the removed name fields)."""
        return self.fullname
