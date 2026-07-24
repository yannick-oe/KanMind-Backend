"""Tests for the task-comment endpoints."""

from rest_framework.test import APITestCase

from kanban_app.models import Comment

from .helpers import (
    COMMENT_FIELD_ORDER,
    comment_detail_url,
    make_board,
    make_comment,
    make_task,
    make_user,
    task_comments_url,
)


class CommentListTests(APITestCase):
    """Cover GET /api/tasks/{id}/comments/."""

    def setUp(self):
        """Create a board, a member and a task."""
        self.owner = make_user("o@x.com")
        self.member = make_user("m@x.com")
        self.board = make_board(self.owner, members=[self.member])
        self.task = make_task(self.board)

    def test_non_participant_is_403(self):
        """A stranger cannot read the comments."""
        self.client.force_authenticate(user=make_user("s@x.com"))
        response = self.client.get(task_comments_url(self.task.id))
        self.assertEqual(response.status_code, 403)

    def test_missing_task_is_404(self):
        """Comments of a non-existent task return 404."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(task_comments_url(9999))
        self.assertEqual(response.status_code, 404)

    def test_returns_comments_in_chronological_order(self):
        """Comments come back oldest first with the right shape."""
        make_comment(self.task, self.member, content="first")
        make_comment(self.task, self.owner, content="second")
        self.client.force_authenticate(user=self.member)
        body = self.client.get(task_comments_url(self.task.id)).json()
        self.assertEqual([c["content"] for c in body], ["first", "second"])
        self.assertEqual(list(body[0].keys()), COMMENT_FIELD_ORDER)
        self.assertEqual(body[0]["author"], self.member.fullname)


class CommentCreateTests(APITestCase):
    """Cover POST /api/tasks/{id}/comments/."""

    def setUp(self):
        """Create a board, a member and a task."""
        self.owner = make_user("o@x.com")
        self.member = make_user("m@x.com")
        self.board = make_board(self.owner, members=[self.member])
        self.task = make_task(self.board)

    def test_non_participant_is_403(self):
        """A stranger cannot post a comment."""
        self.client.force_authenticate(user=make_user("s@x.com"))
        response = self.client.post(
            task_comments_url(self.task.id),
            {"content": "hi"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_creates_comment_with_author_from_user(self):
        """The author is the request user, not the request body."""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            task_comments_url(self.task.id),
            {"content": "hello", "author": "spoofed"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.json().keys()), COMMENT_FIELD_ORDER)
        self.assertEqual(response.json()["author"], self.member.fullname)

    def test_empty_content_is_400(self):
        """Whitespace-only content is rejected with 400."""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            task_comments_url(self.task.id),
            {"content": "   "},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_blank_content_is_400(self):
        """Truly empty content is rejected with 400."""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            task_comments_url(self.task.id),
            {"content": ""},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class CommentDeleteTests(APITestCase):
    """Cover DELETE /api/tasks/{id}/comments/{comment_id}/."""

    def setUp(self):
        """Create a board, a member, a task and a comment."""
        self.owner = make_user("o@x.com")
        self.member = make_user("m@x.com")
        self.board = make_board(self.owner, members=[self.member])
        self.task = make_task(self.board)
        self.comment = make_comment(self.task, self.member)

    def test_author_deletes_with_204(self):
        """The author deletes their comment and gets 204."""
        self.client.force_authenticate(user=self.member)
        url = comment_detail_url(self.task.id, self.comment.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Comment.objects.exists())

    def test_board_owner_is_not_the_author_and_gets_403(self):
        """Even the board owner cannot delete another's comment."""
        self.client.force_authenticate(user=self.owner)
        url = comment_detail_url(self.task.id, self.comment.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_comment_of_another_task_is_404(self):
        """A comment id under the wrong task is 404, not 204."""
        other_task = make_task(self.board)
        self.client.force_authenticate(user=self.member)
        url = comment_detail_url(other_task.id, self.comment.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
