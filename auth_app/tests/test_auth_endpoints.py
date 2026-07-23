"""Tests for the registration and login API endpoints."""

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import User

REGISTRATION_URL = "/api/registration/"
LOGIN_URL = "/api/login/"
RESPONSE_FIELD_ORDER = ["token", "fullname", "email", "user_id"]
VALID_PASSWORD = "secretpass"
EMAIL = "ada@example.com"
FULLNAME = "Ada Lovelace"


def registration_payload(**overrides):
    """Return a valid registration payload with optional overrides."""
    payload = {
        "fullname": FULLNAME,
        "email": EMAIL,
        "password": VALID_PASSWORD,
        "repeated_password": VALID_PASSWORD,
    }
    payload.update(overrides)
    return payload


class RegistrationEndpointTests(APITestCase):
    """Cover the POST /api/registration/ contract."""

    def test_success_returns_201_and_field_order(self):
        """A valid payload creates a user and returns the token."""
        response = self.client.post(
            REGISTRATION_URL, registration_payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list(response.json().keys()), RESPONSE_FIELD_ORDER)
        self.assertTrue(User.objects.filter(email=EMAIL).exists())

    def test_duplicate_email_returns_400(self):
        """Registering an existing email is rejected with 400."""
        User.objects.create_user(
            email=EMAIL, fullname=FULLNAME, password=VALID_PASSWORD
        )
        response = self.client.post(
            REGISTRATION_URL, registration_payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch_returns_400(self):
        """Mismatched password fields are rejected with 400."""
        response = self.client.post(
            REGISTRATION_URL,
            registration_payload(repeated_password="different"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_field_returns_400(self):
        """A payload missing a required field is rejected with 400."""
        response = self.client.post(
            REGISTRATION_URL, {"email": EMAIL}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginEndpointTests(APITestCase):
    """Cover the POST /api/login/ contract."""

    def setUp(self):
        """Create a user to authenticate against."""
        self.user = User.objects.create_user(
            email=EMAIL, fullname=FULLNAME, password=VALID_PASSWORD
        )

    def test_success_returns_200_and_field_order(self):
        """Valid credentials return 200 and the ordered payload."""
        response = self.client.post(
            LOGIN_URL,
            {"email": EMAIL, "password": VALID_PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.json().keys()), RESPONSE_FIELD_ORDER)

    def test_wrong_password_returns_400_not_401(self):
        """Invalid credentials return 400, never 401."""
        response = self.client.post(
            LOGIN_URL,
            {"email": EMAIL, "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_email_returns_400(self):
        """An unknown email returns 400."""
        response = self.client.post(
            LOGIN_URL,
            {"email": "ghost@example.com", "password": VALID_PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
