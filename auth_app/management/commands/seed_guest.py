"""Management command that seeds the delivered frontend guest user."""

import os

from django.core.management.base import BaseCommand

from auth_app.models import User

DEFAULT_GUEST_EMAIL = "kevin@kovacsi.de"
DEFAULT_GUEST_PASSWORD = "asdasdasd"
GUEST_FULLNAME = "Kevin Kovacsi"


class Command(BaseCommand):
    """Create the hardcoded frontend guest user idempotently."""

    help = "Create the guest user the delivered frontend logs in as."

    def handle(self, *args, **options):
        """Create the guest user or report that it already exists."""
        email = os.getenv("GUEST_EMAIL", DEFAULT_GUEST_EMAIL)
        password = os.getenv("GUEST_PASSWORD", DEFAULT_GUEST_PASSWORD)
        if User.objects.filter(email=email).exists():
            self.stdout.write(f"Guest user {email} already exists.")
            return
        User.objects.create_user(
            email=email, fullname=GUEST_FULLNAME, password=password
        )
        self.stdout.write(f"Created guest user {email}.")
