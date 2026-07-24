"""Application configuration for the kanban_app."""

from django.apps import AppConfig


class KanbanAppConfig(AppConfig):
    """Configure the kanban board application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "kanban_app"
    verbose_name = "Kanban"
