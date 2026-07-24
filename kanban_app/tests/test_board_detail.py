"""Tests for GET /api/boards/{id}/ (detail shape and access)."""

from rest_framework.test import APITestCase

from .helpers import board_detail_url, make_board, make_task, make_user

DETAIL_FIELD_ORDER = ["id", "title", "owner_id", "members", "tasks"]
TASK_FIELD_ORDER = [
    "id",
    "title",
    "description",
    "status",
    "priority",
    "assignee",
    "reviewer",
    "due_date",
    "comments_count",
]


class BoardDetailTests(APITestCase):
    """Cover the board detail endpoint."""

    def setUp(self):
        """Create an owner and a board for each test."""
        self.owner = make_user("o@x.com")
        self.board = make_board(self.owner, title="B")

    def test_missing_board_returns_404(self):
        """A non-existent board is 404 even for a valid user."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(board_detail_url(9999))
        self.assertEqual(response.status_code, 404)

    def test_stranger_returns_403(self):
        """An existing board a stranger cannot see returns 403."""
        self.client.force_authenticate(user=make_user("s@x.com"))
        response = self.client.get(board_detail_url(self.board.id))
        self.assertEqual(response.status_code, 403)

    def test_owner_gets_detail_shape(self):
        """The owner sees the detail shape with nested users."""
        assignee = make_user("a@x.com")
        make_task(self.board, assignee=assignee)
        self.client.force_authenticate(user=self.owner)
        data = self.client.get(board_detail_url(self.board.id)).json()
        self.assertEqual(list(data.keys()), DETAIL_FIELD_ORDER)
        task = data["tasks"][0]
        self.assertNotIn("board", task)
        self.assertEqual(task["assignee"]["email"], "a@x.com")

    def test_task_field_order_and_null_reviewer(self):
        """Task fields keep order; an unset reviewer is null."""
        make_task(self.board)
        self.client.force_authenticate(user=self.owner)
        data = self.client.get(board_detail_url(self.board.id)).json()
        task = data["tasks"][0]
        self.assertEqual(list(task.keys()), TASK_FIELD_ORDER)
        self.assertIsNone(task["reviewer"])
