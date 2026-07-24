"""API views for registration, login and email lookup."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import User
from .serializers import (
    AuthResponseSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserNestedSerializer,
)

EMAIL_REQUIRED_ERROR = "The email query parameter is required."
EMAIL_MALFORMED_ERROR = "The email address is malformed."


def build_auth_response_data(user, token):
    """Build the ordered auth payload for both auth endpoints."""
    payload = {"token": token.key, "user": user}
    return AuthResponseSerializer(payload).data


def normalize_email_param(raw):
    """Restore a '+' that arrived URL-decoded as a space."""
    return raw.strip().replace(" ", "+")


def validate_email_param(email):
    """Reject a missing or malformed email with a 400 error."""
    if not email:
        raise ValidationError(EMAIL_REQUIRED_ERROR)
    try:
        django_validate_email(email)
    except DjangoValidationError:
        raise ValidationError(EMAIL_MALFORMED_ERROR)


class RegistrationView(APIView):
    """Register a new user and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create a user and return the auth payload with 201."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        data = build_auth_response_data(user, token)
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate an existing user and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate a user and return the auth payload with 200."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        data = build_auth_response_data(user, token)
        return Response(data, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """Look up a single user by email address."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the user matching the email or an error code."""
        email = normalize_email_param(request.query_params.get("email", ""))
        validate_email_param(email)
        user = get_object_or_404(User, email__iexact=email)
        return Response(UserNestedSerializer(user).data)
