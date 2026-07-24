"""Query-correctness and query-count tests for the kanban API."""

from rest_framework.test import APITestCase

from kanban_app.models import TaskPriority, TaskStatus

from .helpers import (
    ASSIGNED_URL,
    BOARDS_URL,
    board_detail_url,
    make_board,
    make_comment,
    make_task,
    make_user,
    task_comments_url,
)

DETAIL_QUERY_COUNT = 3
ASSIGNED_QUERY_COUNT = 1
COMMENT_LIST_QUERY_COUNT = 3


class BoardCountAccuracyTests(APITestCase):
    """Prove the count fields do not fan out across relations."""

    def test_member_and_ticket_counts_do_not_fan_out(self):
        """Two members and three tasks must not multiply counts."""
        owner = make_user("o@x.com")
        members = [make_user("m1@x.com"), make_user("m2@x.com")]
        board = make_board(owner, members=members)
        make_task(board, TaskStatus.TODO, TaskPriority.HIGH)
        make_task(board, TaskStatus.TODO, TaskPriority.LOW)
        make_task(board, TaskStatus.DONE, TaskPriority.LOW)
        self.client.force_authenticate(user=owner)
        item = self.client.get(BOARDS_URL).json()[0]
        self.assertEqual(item["member_count"], 2)
        self.assertEqual(item["ticket_count"], 3)
        self.assertEqual(item["tasks_to_do_count"], 2)
        self.assertEqual(item["tasks_high_prio_count"], 1)


class BoardDetailQueryCountTests(APITestCase):
    """Board detail stays constant even once comments exist."""

    def test_detail_query_count_is_constant_with_comments(self):
        """5 members, 20 tasks and comments still cost 3 queries."""
        owner = make_user("o@x.com")
        members = [make_user(f"m{i}@x.com") for i in range(5)]
        board = make_board(owner, members=members)
        tasks = [make_task(board) for _ in range(20)]
        make_comment(tasks[0], owner)
        make_comment(tasks[0], owner)
        make_comment(tasks[1], owner)
        self.client.force_authenticate(user=owner)
        with self.assertNumQueries(DETAIL_QUERY_COUNT):
            response = self.client.get(board_detail_url(board.id))
        self.assertEqual(response.status_code, 200)


class TaskListQueryCountTests(APITestCase):
    """The assigned-to-me list resolves in a single query."""

    def test_assigned_to_me_query_count(self):
        """20 assigned tasks resolve in one data query."""
        owner = make_user("o@x.com")
        me = make_user("me@x.com")
        board = make_board(owner, members=[me])
        for _ in range(20):
            make_task(board, assignee=me)
        self.client.force_authenticate(user=me)
        with self.assertNumQueries(ASSIGNED_QUERY_COUNT):
            response = self.client.get(ASSIGNED_URL)
        self.assertEqual(response.status_code, 200)


class CommentListQueryCountTests(APITestCase):
    """The comment list is flat in the number of comments."""

    def test_comment_list_query_count(self):
        """10 comments cost a constant number of queries."""
        owner = make_user("o@x.com")
        member = make_user("m@x.com")
        board = make_board(owner, members=[member])
        task = make_task(board)
        for _ in range(10):
            make_comment(task, member)
        self.client.force_authenticate(user=member)
        with self.assertNumQueries(COMMENT_LIST_QUERY_COUNT):
            response = self.client.get(task_comments_url(task.id))
        self.assertEqual(response.status_code, 200)
