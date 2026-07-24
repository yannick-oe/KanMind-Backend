"""Tests for PATCH and DELETE /api/tasks/{task_id}/."""

from rest_framework.test import APITestCase

from kanban_app.models import Comment, Task

from .helpers import (
    TASK_PATCH_FIELD_ORDER,
    make_board,
    make_comment,
    make_task,
    make_user,
    task_detail_url,
)


class TaskPatchTests(APITestCase):
    """Cover the partial task update endpoint."""

    def setUp(self):
        """Create an owner, a member, a board and a task."""
        self.owner = make_user("o@x.com")
        self.member = make_user("m@x.com")
        self.board = make_board(self.owner, members=[self.member])
        self.task = make_task(self.board, title="Old")

    def test_non_participant_is_403(self):
        """A stranger cannot update the task."""
        self.client.force_authenticate(user=make_user("s@x.com"))
        response = self.client.patch(
            task_detail_url(self.task.id),
            {"status": "done"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_single_field_partial_update_and_shape(self):
        """A lone status update succeeds and returns the shape."""
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            task_detail_url(self.task.id),
            {"status": "in-progress"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json().keys()), TASK_PATCH_FIELD_ORDER)
        self.assertEqual(response.json()["status"], "in-progress")

    def test_board_echo_equal_is_accepted(self):
        """Sending the task's own board id is accepted."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            task_detail_url(self.task.id),
            {"board": self.board.id, "title": "New"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "New")

    def test_board_change_is_rejected(self):
        """Sending a different board id is rejected with 400."""
        other = make_board(self.owner, title="Other")
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            task_detail_url(self.task.id),
            {"board": other.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_null_assignee_clears_the_field(self):
        """An explicit null assignee_id clears the assignee."""
        self.task.assignee = self.member
        self.task.save(update_fields=["assignee"])
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            task_detail_url(self.task.id),
            {"assignee_id": None},
            format="json",
        )
        self.assertIsNone(response.json()["assignee"])

    def test_non_member_reviewer_is_rejected(self):
        """A reviewer outside the board is rejected with 400."""
        outsider = make_user("out@x.com")
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            task_detail_url(self.task.id),
            {"reviewer_id": outsider.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class TaskDeleteTests(APITestCase):
    """Cover the task delete endpoint."""

    def setUp(self):
        """Create an owner, a member and a board with a task."""
        self.owner = make_user("o@x.com")
        self.member = make_user("m@x.com")
        self.board = make_board(self.owner, members=[self.member])
        self.creator = make_user("c@x.com")
        self.board.members.add(self.creator)
        self.task = make_task(self.board, created_by=self.creator)

    def test_plain_member_cannot_delete(self):
        """A member who did not create the task gets 403."""
        self.client.force_authenticate(user=self.member)
        response = self.client.delete(task_detail_url(self.task.id))
        self.assertEqual(response.status_code, 403)

    def test_creator_deletes_and_cascades_comments(self):
        """The creator deletes the task; comments cascade."""
        make_comment(self.task, self.creator)
        self.client.force_authenticate(user=self.creator)
        response = self.client.delete(task_detail_url(self.task.id))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
        self.assertFalse(Comment.objects.exists())

    def test_board_owner_can_delete(self):
        """The board owner may delete a task they did not create."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(task_detail_url(self.task.id))
        self.assertEqual(response.status_code, 204)
