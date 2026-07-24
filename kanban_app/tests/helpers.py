"""Shared factory helpers for the kanban tests."""

from datetime import date

from auth_app.models import User
from kanban_app.models import Board, Task, TaskPriority, TaskStatus

DEFAULT_PASSWORD = "secretpass"
DEFAULT_DUE_DATE = date(2026, 12, 31)
BOARDS_URL = "/api/boards/"


def board_detail_url(board_id):
    """Return the detail URL for a board id."""
    return f"/api/boards/{board_id}/"


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
