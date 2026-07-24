"""API views for the task endpoints."""

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Board
from ..permissions import (
    IsTaskBoardParticipant,
    IsTaskCreatorOrBoardOwner,
    user_is_board_participant,
)
from ..selectors import (
    assigned_tasks_queryset,
    reviewing_tasks_queryset,
    task_detail_queryset,
    task_list_queryset,
)
from ..serializers import (
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateResponseSerializer,
    TaskUpdateSerializer,
)

BOARD_REQUIRED_ERROR = "A valid board id is required."


class AssignedToMeView(generics.ListAPIView):
    """List tasks assigned to the requesting user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer
    pagination_class = None

    def get_queryset(self):
        """Return tasks where the user is the assignee."""
        return assigned_tasks_queryset(self.request.user)


class ReviewingView(generics.ListAPIView):
    """List tasks the requesting user reviews."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer
    pagination_class = None

    def get_queryset(self):
        """Return tasks where the user is the reviewer."""
        return reviewing_tasks_queryset(self.request.user)


class TaskCreateView(generics.CreateAPIView):
    """Create a task on a board the user can access."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskCreateSerializer

    def create(self, request, *args, **kwargs):
        """Validate board access, create the task, return it."""
        board = self._resolve_board(request)
        serializer = TaskCreateSerializer(
            data=request.data, context=self._board_context(board)
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save(created_by=request.user, board=board)
        return Response(
            self._list_representation(task.pk),
            status=status.HTTP_201_CREATED,
        )

    def _resolve_board(self, request):
        """Return the requested board or raise 400/403/404."""
        board = get_object_or_404(Board, pk=self._board_pk(request))
        if not user_is_board_participant(request.user, board):
            raise PermissionDenied()
        return board

    def _board_pk(self, request):
        """Extract a valid integer board id or raise 400."""
        board = request.data.get("board")
        if isinstance(board, bool):
            raise ValidationError({"board": [BOARD_REQUIRED_ERROR]})
        if isinstance(board, int):
            return board
        if isinstance(board, str) and board.isdigit():
            return int(board)
        raise ValidationError({"board": [BOARD_REQUIRED_ERROR]})

    def _board_context(self, board):
        """Build serializer context including the resolved board."""
        context = self.get_serializer_context()
        context["board"] = board
        return context

    def _list_representation(self, task_pk):
        """Serialize the created task in the list shape."""
        task = task_list_queryset().get(pk=task_pk)
        return TaskListSerializer(task).data


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Partially update or delete a single task."""

    lookup_url_kwarg = "task_id"
    serializer_class = TaskUpdateSerializer
    http_method_names = ["patch", "delete", "head", "options"]

    def get_queryset(self):
        """Return tasks with related users and board loaded."""
        return task_detail_queryset()

    def get_permissions(self):
        """Creator-or-owner for delete, participant otherwise."""
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardParticipant()]

    def update(self, request, *args, **kwargs):
        """Apply a partial update and return the task shape."""
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskUpdateResponseSerializer(task).data)
