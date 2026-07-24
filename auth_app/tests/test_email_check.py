"""Tests for the GET /api/email-check/ endpoint."""

from rest_framework.test import APITestCase

from auth_app.models import User

EMAIL_CHECK_URL = "/api/email-check/"


def make_user(email, fullname="Test User"):
    """Create a user with a default password."""
    return User.objects.create_user(
        email=email, fullname=fullname, password="secretpass"
    )


class EmailCheckTests(APITestCase):
    """Cover the email-check contract."""

    def test_requires_authentication(self):
        """An unauthenticated request is rejected with 401."""
        response = self.client.get(EMAIL_CHECK_URL, {"email": "a@x.com"})
        self.assertEqual(response.status_code, 401)

    def test_missing_email_returns_400(self):
        """A request without an email is rejected with 400."""
        self.client.force_authenticate(user=make_user("u@x.com"))
        response = self.client.get(EMAIL_CHECK_URL)
        self.assertEqual(response.status_code, 400)

    def test_malformed_email_returns_400(self):
        """A malformed email is rejected with 400."""
        self.client.force_authenticate(user=make_user("u@x.com"))
        response = self.client.get(EMAIL_CHECK_URL, {"email": "not-an-email"})
        self.assertEqual(response.status_code, 400)

    def test_plus_address_arriving_as_space_is_restored(self):
        """A '+' decoded to a space is restored so the user resolves."""
        target = make_user("plus+tag@x.com", fullname="Plus Tag")
        self.client.force_authenticate(user=make_user("u@x.com"))
        response = self.client.get("/api/email-check/?email=plus+tag@x.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], target.id)

    def test_malformed_with_space_still_returns_400(self):
        """A genuinely malformed value with a space stays a 400."""
        self.client.force_authenticate(user=make_user("u@x.com"))
        response = self.client.get(EMAIL_CHECK_URL, {"email": "john doe"})
        self.assertEqual(response.status_code, 400)

    def test_unknown_email_returns_404(self):
        """An unknown address returns 404, never 200 with a flag."""
        self.client.force_authenticate(user=make_user("u@x.com"))
        response = self.client.get(EMAIL_CHECK_URL, {"email": "ghost@x.com"})
        self.assertEqual(response.status_code, 404)

    def test_known_email_returns_user_shape(self):
        """A known address returns the id/email/fullname object."""
        make_user("target@x.com", fullname="Tar Get")
        self.client.force_authenticate(user=make_user("u@x.com"))
        response = self.client.get(EMAIL_CHECK_URL, {"email": "target@x.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.json().keys()), ["id", "email", "fullname"]
        )
