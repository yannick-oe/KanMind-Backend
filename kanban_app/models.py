"""Data structures for the kanban application."""

from django.conf import settings
from django.db import models

TITLE_MAX_LENGTH = 255
STATUS_MAX_LENGTH = 20
PRIORITY_MAX_LENGTH = 10


class TaskStatus(models.TextChoices):
    """Allowed task workflow states (lowercase, hyphenated)."""

    TODO = "to-do", "To do"
    IN_PROGRESS = "in-progress", "In progress"
    REVIEW = "review", "Review"
    DONE = "done", "Done"


class TaskPriority(models.TextChoices):
    """Allowed task priority levels."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class Board(models.Model):
    """A kanban board owned by a user and shared with members."""

    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="boards",
        blank=True,
    )

    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ["id"]

    def __str__(self) -> str:
        """Return the board title."""
        return self.title


class Task(models.Model):
    """A single task belonging to a board."""

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    description = models.TextField()
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH, choices=TaskStatus.choices
    )
    priority = models.CharField(
        max_length=PRIORITY_MAX_LENGTH, choices=TaskPriority.choices
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewing_tasks",
    )
    due_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["id"]

    def __str__(self) -> str:
        """Return the task title."""
        return self.title


class Comment(models.Model):
    """A comment written by a user on a task."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]

    def __str__(self) -> str:
        """Return a short label for the comment."""
        return f"Comment {self.pk} on task {self.task_id}"
