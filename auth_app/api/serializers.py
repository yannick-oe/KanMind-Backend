"""Serializers for registration, login and the auth response."""

from django.contrib.auth import authenticate
from rest_framework import serializers

from ..models import User

PASSWORD_MISMATCH_ERROR = "The passwords do not match."
INVALID_CREDENTIALS_ERROR = "Invalid email or password."


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration input and create a new user."""

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]

    def validate(self, attrs):
        """Reject payloads whose password fields do not match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": [PASSWORD_MISMATCH_ERROR]}
            )
        return attrs

    def create(self, validated_data):
        """Create the user with a hashed password."""
        validated_data.pop("repeated_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Authenticate a user by email and password."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the credentials or raise a 400 error."""
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError(INVALID_CREDENTIALS_ERROR)
        attrs["user"] = user
        return attrs


class AuthResponseSerializer(serializers.Serializer):
    """Serialize the auth payload in the contracted field order."""

    token = serializers.CharField()
    fullname = serializers.CharField(source="user.fullname")
    email = serializers.EmailField(source="user.email")
    user_id = serializers.IntegerField(source="user.id")


class UserNestedSerializer(serializers.ModelSerializer):
    """Compact user representation reused across the API."""

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
