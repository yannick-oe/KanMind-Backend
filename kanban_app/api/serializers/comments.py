"""Serializers for the comment endpoints."""

from rest_framework import serializers

from ...models import Comment

EMPTY_CONTENT_ERROR = "The comment content must not be empty."


class CommentSerializer(serializers.ModelSerializer):
    """Comment representation for listing and creation."""

    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["id", "created_at"]

    def validate_content(self, value):
        """Reject empty or whitespace-only content."""
        if not value.strip():
            raise serializers.ValidationError(EMPTY_CONTENT_ERROR)
        return value
