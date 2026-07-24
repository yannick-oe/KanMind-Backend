"""Access-control rules for the board endpoints."""

from rest_framework.permissions import BasePermission


class IsBoardOwnerOrMember(BasePermission):
    """Allow access to a board's owner or one of its members."""

    def has_object_permission(self, request, view, obj):
        """Grant access when the user owns or belongs to the board."""
        user_id = request.user.id
        if obj.owner_id == user_id:
            return True
        return any(member.id == user_id for member in obj.members.all())


class IsBoardOwner(BasePermission):
    """Allow access only to a board's owner."""

    def has_object_permission(self, request, view, obj):
        """Grant access only when the user owns the board."""
        return obj.owner_id == request.user.id
