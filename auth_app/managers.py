"""Manager for the email-based custom user model."""

from django.contrib.auth.models import BaseUserManager

EMAIL_REQUIRED_ERROR = "The email address is required."
FULLNAME_REQUIRED_ERROR = "The fullname is required."
STAFF_ERROR = "Superuser must have is_staff=True."
SUPERUSER_ERROR = "Superuser must have is_superuser=True."


class CustomUserManager(BaseUserManager):
    """Create users and superusers keyed by email instead of username."""

    def create_user(self, email, fullname, password=None, **extra):
        """Create and persist a user with a hashed password."""
        if not email:
            raise ValueError(EMAIL_REQUIRED_ERROR)
        if not fullname:
            raise ValueError(FULLNAME_REQUIRED_ERROR)
        email = self.normalize_email(email)
        user = self.model(email=email, fullname=fullname, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None, **extra):
        """Create and persist a superuser with staff permissions."""
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_staff") is not True:
            raise ValueError(STAFF_ERROR)
        if extra.get("is_superuser") is not True:
            raise ValueError(SUPERUSER_ERROR)
        return self.create_user(email, fullname, password, **extra)
