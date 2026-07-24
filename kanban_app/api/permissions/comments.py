"""Comment access-control rules."""

from rest_framework.permissions import BasePermission


class IsCommentAuthor(BasePermission):
    """Allow access only to the comment's author."""

    def has_object_permission(self, request, view, obj):
        """Grant access only to the user who wrote the comment."""
        return obj.author_id == request.user.id
