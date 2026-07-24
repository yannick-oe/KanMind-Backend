"""Tests for GET /api/tasks/assigned-to-me/ and /reviewing/."""

from rest_framework.test import APITestCase

from .helpers import (
    ASSIGNED_URL,
    REVIEWING_URL,
    TASK_LIST_FIELD_ORDER,
    make_board,
    make_task,
    make_user,
)


class AssignedToMeTests(APITestCase):
    """Cover the assigned-to-me list endpoint."""

    def setUp(self):
        """Create an owner, a member and a shared board."""
        self.owner = make_user("o@x.com")
        self.me = make_user("me@x.com")
        self.board = make_board(self.owner, members=[self.me])

    def test_requires_authentication(self):
        """An anonymous request is rejected with 401."""
        response = self.client.get(ASSIGNED_URL)
        self.assertEqual(response.status_code, 401)

    def test_lists_only_tasks_assigned_to_user(self):
        """Only tasks where the user is assignee are returned."""
        make_task(self.board, assignee=self.me, title="Mine")
        make_task(self.board, reviewer=self.me, title="Reviewing")
        self.client.force_authenticate(user=self.me)
        titles = [t["title"] for t in self.client.get(ASSIGNED_URL).json()]
        self.assertEqual(titles, ["Mine"])

    def test_item_field_order_and_board_is_int(self):
        """A task item exposes the contracted fields in order."""
        make_task(self.board, assignee=self.me)
        self.client.force_authenticate(user=self.me)
        item = self.client.get(ASSIGNED_URL).json()[0]
        self.assertEqual(list(item.keys()), TASK_LIST_FIELD_ORDER)
        self.assertEqual(item["board"], self.board.id)


class ReviewingTests(APITestCase):
    """Cover the reviewing list endpoint."""

    def setUp(self):
        """Create an owner, a member and a shared board."""
        self.owner = make_user("o@x.com")
        self.me = make_user("me@x.com")
        self.board = make_board(self.owner, members=[self.me])

    def test_requires_authentication(self):
        """An anonymous request is rejected with 401."""
        response = self.client.get(REVIEWING_URL)
        self.assertEqual(response.status_code, 401)

    def test_lists_only_tasks_reviewed_by_user(self):
        """Only tasks where the user is reviewer are returned."""
        make_task(self.board, reviewer=self.me, title="Review")
        make_task(self.board, assignee=self.me, title="Assigned")
        self.client.force_authenticate(user=self.me)
        titles = [t["title"] for t in self.client.get(REVIEWING_URL).json()]
        self.assertEqual(titles, ["Review"])
