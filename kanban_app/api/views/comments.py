"""API views for the comment endpoints."""

from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from ...models import Comment, Task
from ..permissions import IsCommentAuthor, IsTaskBoardParticipant
from ..selectors import comments_queryset
from ..serializers import CommentSerializer


class TaskCommentsView(generics.ListCreateAPIView):
    """List a task's comments or add a new comment."""

    permission_classes = [IsAuthenticated, IsTaskBoardParticipant]
    serializer_class = CommentSerializer
    pagination_class = None

    def get_task(self):
        """Return the URL task (cached), enforcing board access."""
        if not hasattr(self, "_task"):
            task = get_object_or_404(
                Task.objects.select_related("board"),
                pk=self.kwargs["task_id"],
            )
            self.check_object_permissions(self.request, task)
            self._task = task
        return self._task

    def get_queryset(self):
        """Return the task's comments in chronological order."""
        return comments_queryset(self.get_task())

    def create(self, request, *args, **kwargs):
        """Check board access before validating the comment."""
        self.get_task()
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Persist the comment with the request user as author."""
        serializer.save(author=self.request.user, task=self.get_task())


class CommentDeleteView(generics.DestroyAPIView):
    """Delete a comment authored by the requesting user."""

    permission_classes = [IsAuthenticated, IsCommentAuthor]
    serializer_class = CommentSerializer
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        """Scope comments to the task named in the URL."""
        return Comment.objects.filter(task_id=self.kwargs["task_id"])
