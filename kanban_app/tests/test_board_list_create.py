"""Tests for GET and POST /api/boards/."""

from rest_framework.test import APITestCase

from kanban_app.models import Board

from .helpers import BOARDS_URL, make_board, make_user

LIST_FIELD_ORDER = [
    "id",
    "title",
    "member_count",
    "ticket_count",
    "tasks_to_do_count",
    "tasks_high_prio_count",
    "owner_id",
]


class BoardListTests(APITestCase):
    """Cover the board list endpoint."""

    def test_requires_authentication(self):
        """An anonymous request is rejected with 401."""
        response = self.client.get(BOARDS_URL)
        self.assertEqual(response.status_code, 401)

    def test_lists_only_owner_or_member_boards(self):
        """The list omits boards the user neither owns nor joins."""
        owner = make_user("o@x.com")
        make_board(owner, title="Mine")
        make_board(make_user("x@x.com"), title="Theirs")
        viewer = make_user("v@x.com")
        make_board(owner, members=[viewer], title="Shared")
        self.client.force_authenticate(user=viewer)
        titles = {b["title"] for b in self.client.get(BOARDS_URL).json()}
        self.assertEqual(titles, {"Shared"})

    def test_list_item_field_order(self):
        """A list item exposes the contracted fields in order."""
        owner = make_user("o@x.com")
        make_board(owner)
        self.client.force_authenticate(user=owner)
        item = self.client.get(BOARDS_URL).json()[0]
        self.assertEqual(list(item.keys()), LIST_FIELD_ORDER)


class BoardCreateTests(APITestCase):
    """Cover the board create endpoint."""

    def test_requires_authentication(self):
        """An anonymous create is rejected with 401."""
        response = self.client.post(BOARDS_URL, {"title": "B"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_creates_board_without_auto_adding_owner(self):
        """The owner is not silently added to the member list."""
        owner = make_user("o@x.com")
        member = make_user("m@x.com")
        self.client.force_authenticate(user=owner)
        payload = {"title": "B", "members": [member.id]}
        response = self.client.post(BOARDS_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["member_count"], 1)
        board = Board.objects.get(pk=response.json()["id"])
        self.assertNotIn(owner, board.members.all())

    def test_create_response_field_order(self):
        """The create response matches the list item field order."""
        owner = make_user("o@x.com")
        self.client.force_authenticate(user=owner)
        response = self.client.post(BOARDS_URL, {"title": "B"}, format="json")
        self.assertEqual(list(response.json().keys()), LIST_FIELD_ORDER)
