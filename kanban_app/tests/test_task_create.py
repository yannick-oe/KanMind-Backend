"""Tests for POST /api/tasks/."""

from rest_framework.test import APITestCase

from kanban_app.models import Task

from .helpers import (
    TASK_LIST_FIELD_ORDER,
    TASKS_URL,
    make_board,
    make_user,
)


def task_payload(board, **overrides):
    """Return a valid task-create payload with optional overrides."""
    payload = {
        "board": board.id,
        "title": "Task",
        "description": "Body",
        "status": "to-do",
        "priority": "high",
        "assignee_id": None,
        "reviewer_id": None,
        "due_date": "2026-12-31",
    }
    payload.update(overrides)
    return payload


class TaskCreateTests(APITestCase):
    """Cover the task-create endpoint."""

    def setUp(self):
        """Create an owner, a member and a shared board."""
        self.owner = make_user("o@x.com")
        self.member = make_user("m@x.com")
        self.board = make_board(self.owner, members=[self.member])

    def test_requires_authentication(self):
        """An anonymous create is rejected with 401."""
        response = self.client.post(
            TASKS_URL, task_payload(self.board), format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_owner_creates_task_with_field_order(self):
        """The owner creates a task and gets the list shape back."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            TASKS_URL, task_payload(self.board), format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.json().keys()), TASK_LIST_FIELD_ORDER)
        self.assertEqual(response.json()["comments_count"], 0)

    def test_null_assignee_is_accepted(self):
        """An explicit null assignee_id is accepted."""
        self.client.force_authenticate(user=self.owner)
        payload = task_payload(self.board, assignee_id=None)
        response = self.client.post(TASKS_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["assignee"])

    def test_non_member_assignee_is_rejected(self):
        """An assignee outside the board is rejected with 400."""
        outsider = make_user("out@x.com")
        self.client.force_authenticate(user=self.owner)
        payload = task_payload(self.board, assignee_id=outsider.id)
        response = self.client.post(TASKS_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_priority_is_rejected(self):
        """An out-of-choices priority is rejected with 400."""
        self.client.force_authenticate(user=self.owner)
        payload = task_payload(self.board, priority="urgent")
        response = self.client.post(TASKS_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_no_board_access_is_403(self):
        """A user with no access to the board gets 403."""
        stranger = make_user("s@x.com")
        self.client.force_authenticate(user=stranger)
        response = self.client.post(
            TASKS_URL, task_payload(self.board), format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_missing_board_is_404(self):
        """A non-existent board id yields 404."""
        self.client.force_authenticate(user=self.owner)
        payload = task_payload(self.board)
        payload["board"] = 9999
        response = self.client.post(TASKS_URL, payload, format="json")
        self.assertEqual(response.status_code, 404)

    def test_created_by_is_the_request_user(self):
        """created_by is taken from the authenticated user."""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            TASKS_URL, task_payload(self.board), format="json"
        )
        task = Task.objects.get(pk=response.json()["id"])
        self.assertEqual(task.created_by, self.member)

    def test_float_board_id_is_rejected(self):
        """A fractional board value is a 400, not a truncated id."""
        self.client.force_authenticate(user=self.owner)
        payload = task_payload(self.board)
        payload["board"] = self.board.id + 0.9
        response = self.client.post(TASKS_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)
