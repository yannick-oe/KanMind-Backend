"""Query builders for the kanban endpoints."""

from django.db.models import (
    Count,
    IntegerField,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
)
from django.db.models.functions import Coalesce

from ..models import Board, Task, TaskPriority, TaskStatus


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


def task_list_queryset():
    """Build the annotated task queryset for the list endpoints."""
    return (
        Task.objects.select_related("assignee", "reviewer")
        .annotate(comments_count=Count("comments", distinct=True))
        .order_by("id")
    )


def assigned_tasks_queryset(user):
    """Return annotated tasks assigned to the given user."""
    return task_list_queryset().filter(assignee=user)


def reviewing_tasks_queryset(user):
    """Return annotated tasks the given user reviews."""
    return task_list_queryset().filter(reviewer=user)


def task_detail_queryset():
    """Build the queryset for task update and delete views."""
    return Task.objects.select_related("board", "assignee", "reviewer")


def comments_queryset(task):
    """Return a task's comments ordered chronologically."""
    return task.comments.select_related("author").order_by("created_at")
