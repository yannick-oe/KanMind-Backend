"""Tests for the kanban model string representations."""

from django.test import TestCase

from .helpers import make_board, make_comment, make_task, make_user


class ModelStrTests(TestCase):
    """Cover the __str__ methods of the kanban models."""

    def setUp(self):
        """Create an owner shared by the model tests."""
        self.owner = make_user("o@x.com")

    def test_board_str_is_its_title(self):
        """A board is represented by its title."""
        board = make_board(self.owner, title="My Board")
        self.assertEqual(str(board), "My Board")

    def test_task_str_is_its_title(self):
        """A task is represented by its title."""
        task = make_task(make_board(self.owner), title="My Task")
        self.assertEqual(str(task), "My Task")

    def test_comment_str_mentions_its_task(self):
        """A comment representation references its task id."""
        task = make_task(make_board(self.owner))
        comment = make_comment(task, self.owner, content="hi")
        self.assertIn(str(task.id), str(comment))
