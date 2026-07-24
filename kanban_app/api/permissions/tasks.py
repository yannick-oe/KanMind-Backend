"""Task access-control rules."""

from rest_framework.permissions import BasePermission

from .boards import user_is_board_participant


class IsTaskBoardParticipant(BasePermission):
    """Allow access to the owner or a member of the task's board."""

    def has_object_permission(self, request, view, obj):
        """Grant access based on the task's board membership."""
        return user_is_board_participant(request.user, obj.board)


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allow deletion by the task creator or the board owner."""

    def has_object_permission(self, request, view, obj):
        """Grant access to the task's creator or the board owner."""
        user_id = request.user.id
        return obj.created_by_id == user_id or obj.board.owner_id == user_id
