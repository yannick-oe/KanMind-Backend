"""API views for the registration and login endpoints."""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AuthResponseSerializer,
    LoginSerializer,
    RegistrationSerializer,
)


def build_auth_response_data(user, token):
    """Build the ordered auth payload for both auth endpoints."""
    payload = {"token": token.key, "user": user}
    return AuthResponseSerializer(payload).data


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
