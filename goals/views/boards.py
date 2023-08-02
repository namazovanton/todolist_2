from rest_framework import generics, permissions, filters
from django.db import transaction

from goals.models import BoardParticipant, Board, Goal
from goals.permissions import BoardPermission
from goals.serializers import BoardSerializer, BoardWithParticipantsSerializer


class BoardCreateView(generics.CreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        with transaction.atomic():
            board = serializer.save()
            BoardParticipant.objects.create(user=self.request.user, board=board)


class BoardListView(generics.ListAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.filter(participants__user=self.request.user).exclude(is_deleted=True)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardWithParticipantsSerializer
    permission_classes = [BoardPermission]

    def get_queryset(self):
        return Board.objects.prefetch_related('participants__user').exclude(is_deleted=True)

    def perform_destroy(self, instance: Board) -> None:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(Goal.Status.archived)

