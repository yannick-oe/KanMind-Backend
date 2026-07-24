"""Shared factory helpers for the kanban tests."""

from datetime import date

from auth_app.models import User
from kanban_app.models import (
    Board,
    Comment,
    Task,
    TaskPriority,
    TaskStatus,
)

DEFAULT_PASSWORD = "secretpass"
DEFAULT_DUE_DATE = date(2026, 12, 31)
BOARDS_URL = "/api/boards/"
TASKS_URL = "/api/tasks/"
ASSIGNED_URL = "/api/tasks/assigned-to-me/"
REVIEWING_URL = "/api/tasks/reviewing/"

TASK_LIST_FIELD_ORDER = [
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
TASK_PATCH_FIELD_ORDER = [
    "id",
    "title",
    "description",
    "status",
    "priority",
    "assignee",
    "reviewer",
    "due_date",
]
COMMENT_FIELD_ORDER = ["id", "created_at", "author", "content"]


def board_detail_url(board_id):
    """Return the detail URL for a board id."""
    return f"/api/boards/{board_id}/"


def task_detail_url(task_id):
    """Return the detail URL for a task id."""
    return f"/api/tasks/{task_id}/"


def task_comments_url(task_id):
    """Return the comments URL for a task id."""
    return f"/api/tasks/{task_id}/comments/"


def comment_detail_url(task_id, comment_id):
    """Return the delete URL for a comment on a task."""
    return f"/api/tasks/{task_id}/comments/{comment_id}/"


def make_user(email, fullname="Test User"):
    """Create and return a user with a default password."""
    return User.objects.create_user(
        email=email, fullname=fullname, password=DEFAULT_PASSWORD
    )


def make_board(owner, members=None, title="Board"):
    """Create a board with an owner and optional members."""
    board = Board.objects.create(title=title, owner=owner)
    if members:
        board.members.set(members)
    return board


def make_task(
    board, status=TaskStatus.TODO, priority=TaskPriority.LOW, **extra
):
    """Create a task on a board with sensible defaults."""
    return Task.objects.create(
        board=board,
        title=extra.pop("title", "Task"),
        description=extra.pop("description", ""),
        status=status,
        priority=priority,
        due_date=extra.pop("due_date", DEFAULT_DUE_DATE),
        **extra,
    )


def make_comment(task, author, content="A comment"):
    """Create a comment on a task."""
    return Comment.objects.create(task=task, author=author, content=content)
