"""Tests for the user manager, model helpers and admin form."""

from django.test import TestCase

from auth_app.admin import UserCreationForm
from auth_app.models import User


class ManagerTests(TestCase):
    """Cover the custom user manager."""

    def test_create_superuser_sets_permission_flags(self):
        """A superuser is created with staff and superuser flags."""
        admin = User.objects.create_superuser(
            email="s@x.com", fullname="Super User", password="secretpass"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password("secretpass"))


class UserModelTests(TestCase):
    """Cover the model string and name helpers."""

    def test_str_and_name_helpers_return_fullname(self):
        """__str__ and the name helpers all return the fullname."""
        user = User.objects.create_user(
            email="a@x.com", fullname="Ada Lovelace", password="secretpass"
        )
        self.assertEqual(str(user), "Ada Lovelace")
        self.assertEqual(user.get_full_name(), "Ada Lovelace")
        self.assertEqual(user.get_short_name(), "Ada Lovelace")


class UserCreationFormTests(TestCase):
    """Cover the admin form that creates users."""

    def _data(self, **overrides):
        """Return admin create-form data with optional overrides."""
        data = {
            "email": "new@x.com",
            "fullname": "New User",
            "password1": "secretpass",
            "password2": "secretpass",
        }
        data.update(overrides)
        return data

    def test_valid_form_hashes_the_password(self):
        """A valid form creates a user with a hashed password."""
        form = UserCreationForm(data=self._data())
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password("secretpass"))

    def test_mismatched_passwords_are_invalid(self):
        """Mismatched password entries fail validation."""
        form = UserCreationForm(data=self._data(password2="different"))
        self.assertFalse(form.is_valid())
