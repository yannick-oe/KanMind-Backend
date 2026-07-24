"""Serializers for the board endpoints."""

from rest_framework import serializers

from auth_app.api.serializers import UserNestedSerializer
from auth_app.models import User

from ..models import Board, Task


class BoardListSerializer(serializers.ModelSerializer):
    """Board summary with aggregate counts for the list endpoint."""

    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]


class BoardCreateSerializer(serializers.ModelSerializer):
    """Validate and create a board from a title and member ids."""

    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Board
        fields = ["title", "members"]

    def create(self, validated_data):
        """Create the board with the request user as owner."""
        members = validated_data.pop("members", [])
        board = Board.objects.create(
            owner=self.context["request"].user, **validated_data
        )
        board.members.set(members)
        return board


class TaskDetailSerializer(serializers.ModelSerializer):
    """Task representation nested inside the board detail."""

    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

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
            "comments_count",
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Full board detail with members and nested tasks."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserNestedSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Validate a partial board update (title and/or members)."""

    title = serializers.CharField(required=False)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Board
        fields = ["title", "members"]


class BoardPatchResponseSerializer(serializers.ModelSerializer):
    """Board representation returned by the PATCH endpoint."""

    owner_data = UserNestedSerializer(source="owner", read_only=True)
    members_data = UserNestedSerializer(
        source="members", many=True, read_only=True
    )

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data"]
