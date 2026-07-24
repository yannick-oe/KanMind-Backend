"""API views for the board endpoints."""

from django.db.models import (
    Count,
    IntegerField,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
)
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Board, Task, TaskPriority, TaskStatus
from .permissions import IsBoardOwner, IsBoardOwnerOrMember
from .serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardPatchResponseSerializer,
    BoardUpdateSerializer,
)


def _member_count_subquery():
    """Return a correlated subquery counting a board's members."""
    through = Board.members.through
    counts = (
        through.objects.filter(board_id=OuterRef("pk"))
        .values("board_id")
        .annotate(total=Count("id"))
        .values("total")
    )
    return Coalesce(Subquery(counts, output_field=IntegerField()), 0)


def _annotate_counts(queryset):
    """Annotate boards with member and task aggregate counts."""
    return queryset.annotate(
        member_count=_member_count_subquery(),
        ticket_count=Count("tasks", distinct=True),
        tasks_to_do_count=Count(
            "tasks",
            filter=Q(tasks__status=TaskStatus.TODO),
            distinct=True,
        ),
        tasks_high_prio_count=Count(
            "tasks",
            filter=Q(tasks__priority=TaskPriority.HIGH),
            distinct=True,
        ),
    )


def visible_board_ids(user):
    """Return ids of boards where the user is owner or member."""
    return (
        Board.objects.filter(Q(owner=user) | Q(members=user))
        .values("id")
        .distinct()
    )


def board_list_queryset(user):
    """Build the annotated queryset for the board list endpoint."""
    boards = Board.objects.filter(pk__in=visible_board_ids(user))
    return _annotate_counts(boards).order_by("id")


def board_detail_queryset():
    """Build the prefetched queryset for the board detail view."""
    tasks = (
        Task.objects.select_related("assignee", "reviewer")
        .annotate(comments_count=Count("comments", distinct=True))
        .order_by("id")
    )
    return Board.objects.prefetch_related(
        Prefetch("tasks", queryset=tasks), "members"
    )


class BoardListCreateView(generics.ListCreateAPIView):
    """List boards for the user or create a new board."""

    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return boards visible to the requesting user."""
        return board_list_queryset(self.request.user)

    def get_serializer_class(self):
        """Use the create serializer for POST, list otherwise."""
        if self.request.method == "POST":
            return BoardCreateSerializer
        return BoardListSerializer

    def create(self, request, *args, **kwargs):
        """Create a board and return it in the list shape."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        data = self._list_representation(board.pk)
        return Response(data, status=status.HTTP_201_CREATED)

    def _list_representation(self, board_pk):
        """Serialize a created board with its aggregate counts."""
        board = board_list_queryset(self.request.user).get(pk=board_pk)
        return BoardListSerializer(board).data


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update or delete a single board."""

    lookup_url_kwarg = "board_id"
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Prefetch relations for GET; plain queryset otherwise."""
        if self.request.method == "GET":
            return board_detail_queryset()
        return Board.objects.all()

    def get_permissions(self):
        """Owner-only for delete, owner-or-member otherwise."""
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardOwnerOrMember()]

    def get_serializer_class(self):
        """Use the update serializer for PATCH, detail otherwise."""
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def update(self, request, *args, **kwargs):
        """Apply a partial update and return the PATCH shape."""
        board = self.get_object()
        serializer = self.get_serializer(
            board, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self._patch_representation(board.pk))

    def _patch_representation(self, board_pk):
        """Serialize a board in the PATCH response shape."""
        board = (
            Board.objects.select_related("owner")
            .prefetch_related("members")
            .get(pk=board_pk)
        )
        return BoardPatchResponseSerializer(board).data
