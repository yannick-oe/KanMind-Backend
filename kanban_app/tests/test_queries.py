"""Query-correctness and query-count tests for boards."""

from rest_framework.test import APITestCase

from kanban_app.models import TaskPriority, TaskStatus

from .helpers import (
    BOARDS_URL,
    board_detail_url,
    make_board,
    make_task,
    make_user,
)

DETAIL_QUERY_COUNT = 3


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
    """Prove the hot-path detail query count stays constant."""

    def test_detail_query_count_is_constant(self):
        """5 members and 20 tasks resolve in a fixed query count."""
        owner = make_user("o@x.com")
        members = [make_user(f"m{i}@x.com") for i in range(5)]
        board = make_board(owner, members=members)
        for _ in range(20):
            make_task(board)
        self.client.force_authenticate(user=owner)
        with self.assertNumQueries(DETAIL_QUERY_COUNT):
            response = self.client.get(board_detail_url(board.id))
        self.assertEqual(response.status_code, 200)
