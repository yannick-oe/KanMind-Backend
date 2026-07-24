"""Tests for PATCH and DELETE /api/boards/{id}/."""

from rest_framework.test import APITestCase

from kanban_app.models import Comment, Task

from .helpers import board_detail_url, make_board, make_task, make_user

PATCH_FIELD_ORDER = ["id", "title", "owner_data", "members_data"]


class BoardPatchTests(APITestCase):
    """Cover the partial-update endpoint."""

    def setUp(self):
        """Create an owner and a board for each test."""
        self.owner = make_user("o@x.com")
        self.board = make_board(self.owner, title="Old")

    def test_stranger_returns_403(self):
        """A stranger cannot update the board."""
        self.client.force_authenticate(user=make_user("s@x.com"))
        response = self.client.patch(
            board_detail_url(self.board.id), {"title": "New"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_partial_title_update_returns_patch_shape(self):
        """Sending only a title updates it and returns the shape."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            board_detail_url(self.board.id), {"title": "New"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json().keys()), PATCH_FIELD_ORDER)
        self.assertEqual(response.json()["title"], "New")

    def test_partial_members_update_replaces_wholesale(self):
        """Sending only members replaces the whole member list."""
        self.board.members.set([make_user("m1@x.com")])
        replacement = make_user("m2@x.com")
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            board_detail_url(self.board.id),
            {"members": [replacement.id]},
            format="json",
        )
        ids = [m["id"] for m in response.json()["members_data"]]
        self.assertEqual(ids, [replacement.id])


class BoardDeleteTests(APITestCase):
    """Cover the delete endpoint."""

    def setUp(self):
        """Create an owner and a board for each test."""
        self.owner = make_user("o@x.com")
        self.board = make_board(self.owner, title="B")

    def test_member_cannot_delete_returns_403(self):
        """A member who is not the owner cannot delete the board."""
        member = make_user("m@x.com")
        self.board.members.set([member])
        self.client.force_authenticate(user=member)
        response = self.client.delete(board_detail_url(self.board.id))
        self.assertEqual(response.status_code, 403)

    def test_owner_deletes_and_cascades(self):
        """The owner deletes the board; tasks and comments cascade."""
        task = make_task(self.board)
        Comment.objects.create(task=task, author=self.owner, content="hi")
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(board_detail_url(self.board.id))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
        self.assertFalse(Comment.objects.exists())
