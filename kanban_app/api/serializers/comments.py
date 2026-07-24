"""Serializers for the comment endpoints."""

from rest_framework import serializers

from ...models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Comment representation for listing and creation.

    Empty or whitespace-only content is rejected with 400 by the
    ``CharField`` default (``trim_whitespace`` plus ``allow_blank``),
    so no extra validator is needed.
    """

    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["id", "created_at"]
