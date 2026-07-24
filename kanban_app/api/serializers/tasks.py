"""Serializers for the task endpoints."""

from rest_framework import serializers

from auth_app.api.serializers import UserNestedSerializer
from auth_app.models import User

from ...models import Task
from ..permissions import user_is_board_participant

NOT_PARTICIPANT_ERROR = "The user must be the board owner or a board member."
BOARD_CHANGE_ERROR = "The board of a task cannot be changed."


def require_board_participant(board, user, field_name):
    """Reject an assignee/reviewer that is not a board participant."""
    if user is None:
        return
    if not user_is_board_participant(user, board):
        raise serializers.ValidationError(
            {field_name: [NOT_PARTICIPANT_ERROR]}
        )


class TaskListSerializer(serializers.ModelSerializer):
    """Task representation for the list endpoints and POST response."""

    board = serializers.IntegerField(source="board_id", read_only=True)
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Validate and create a task on a board."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]

    def validate(self, attrs):
        """Ensure assignee and reviewer belong to the board."""
        board = self.context["board"]
        require_board_participant(board, attrs.get("assignee"), "assignee_id")
        require_board_participant(board, attrs.get("reviewer"), "reviewer_id")
        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Validate a partial task update."""

    board = serializers.IntegerField(required=False, write_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]

    def validate_board(self, value):
        """Reject a board id that differs from the task's board."""
        if value != self.instance.board_id:
            raise serializers.ValidationError(BOARD_CHANGE_ERROR)
        return value

    def validate(self, attrs):
        """Ensure assignee and reviewer belong to the task's board."""
        board = self.instance.board
        if "assignee" in attrs:
            require_board_participant(board, attrs["assignee"], "assignee_id")
        if "reviewer" in attrs:
            require_board_participant(board, attrs["reviewer"], "reviewer_id")
        return attrs

    def update(self, instance, validated_data):
        """Drop the read-only board echo before applying changes."""
        validated_data.pop("board", None)
        return super().update(instance, validated_data)


class TaskUpdateResponseSerializer(serializers.ModelSerializer):
    """Task representation returned by the PATCH endpoint."""

    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
        ]
