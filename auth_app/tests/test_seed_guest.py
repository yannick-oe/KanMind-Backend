"""Tests for the seed_guest management command."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from auth_app.models import User

GUEST_EMAIL = "kevin@kovacsi.de"


class SeedGuestCommandTests(TestCase):
    """Cover the seed_guest management command."""

    def _run(self):
        """Run seed_guest and return its captured stdout."""
        out = StringIO()
        call_command("seed_guest", stdout=out)
        return out.getvalue()

    def test_creates_guest_user_with_two_word_name(self):
        """The first run creates the guest with a two-word name."""
        output = self._run()
        self.assertIn("Created", output)
        user = User.objects.get(email=GUEST_EMAIL)
        self.assertEqual(len(user.fullname.split()), 2)
        self.assertTrue(user.check_password("asdasdasd"))

    def test_second_run_is_idempotent(self):
        """A second run changes nothing and reports existence."""
        self._run()
        output = self._run()
        self.assertIn("already exists", output)
        self.assertEqual(User.objects.filter(email=GUEST_EMAIL).count(), 1)
