"""Application configuration for the auth_app."""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Configure the custom authentication application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"
    verbose_name = "Authentication"
