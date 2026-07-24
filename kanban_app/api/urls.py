"""URL routes for the board, task and comment endpoints."""

from django.urls import path

from .views import (
    AssignedToMeView,
    BoardDetailView,
    BoardListCreateView,
    CommentDeleteView,
    ReviewingView,
    TaskCommentsView,
    TaskCreateView,
    TaskDetailView,
)

urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
    path(
        "boards/<int:board_id>/",
        BoardDetailView.as_view(),
        name="board-detail",
    ),
    path(
        "tasks/assigned-to-me/",
        AssignedToMeView.as_view(),
        name="tasks-assigned-to-me",
    ),
    path(
        "tasks/reviewing/",
        ReviewingView.as_view(),
        name="tasks-reviewing",
    ),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/<int:task_id>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
        "tasks/<int:task_id>/comments/",
        TaskCommentsView.as_view(),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
