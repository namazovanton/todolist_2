from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from goals.models import GoalComment
from goals.permissions import GoalCommentPermission
from goals.serializers import GoalCommentSerializer, GoalCommentWithUserSerializer


class GoalCommentCreateView(generics.CreateAPIView):
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalCommentListView(generics.ListAPIView):
    serializer_class = GoalCommentWithUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_field = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(
            goal__category__board__participants__user=self.request.user
        )


class GoalCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalCommentWithUserSerializer
    permission_classes = GoalCommentPermission
    queryset = GoalComment.objects.select_related('user')

    def get_queryset(self):
        return GoalComment.objects.select_related('user').filter(
            goal__category__board__participants__user=self.request.user
        )


