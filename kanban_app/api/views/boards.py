"""API views for the board endpoints."""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Board
from ..permissions import IsBoardOwner, IsBoardOwnerOrMember
from ..selectors import board_detail_queryset, board_list_queryset
from ..serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardPatchResponseSerializer,
    BoardUpdateSerializer,
)


class BoardListCreateView(generics.ListCreateAPIView):
    """List boards for the user or create a new board."""

    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return boards visible to the requesting user."""
        return board_list_queryset(self.request.user)

    def get_serializer_class(self):
        """Use the create serializer for POST, list otherwise."""
        if self.request.method == "POST":
            return BoardCreateSerializer
        return BoardListSerializer

    def create(self, request, *args, **kwargs):
        """Create a board and return it in the list shape."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        data = self._list_representation(board.pk)
        return Response(data, status=status.HTTP_201_CREATED)

    def _list_representation(self, board_pk):
        """Serialize a created board with its aggregate counts."""
        board = board_list_queryset(self.request.user).get(pk=board_pk)
        return BoardListSerializer(board).data


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update or delete a single board."""

    lookup_url_kwarg = "board_id"
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Prefetch relations for GET; plain queryset otherwise."""
        if self.request.method == "GET":
            return board_detail_queryset()
        return Board.objects.all()

    def get_permissions(self):
        """Owner-only for delete, owner-or-member otherwise."""
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardOwnerOrMember()]

    def get_serializer_class(self):
        """Use the update serializer for PATCH, detail otherwise."""
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def update(self, request, *args, **kwargs):
        """Apply a partial update and return the PATCH shape."""
        board = self.get_object()
        serializer = self.get_serializer(
            board, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self._patch_representation(board.pk))

    def _patch_representation(self, board_pk):
        """Serialize a board in the PATCH response shape."""
        board = (
            Board.objects.select_related("owner")
            .prefetch_related("members")
            .get(pk=board_pk)
        )
        return BoardPatchResponseSerializer(board).data
