from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from goals.filters import GoalDateFilter
from goals.models import Goal
from goals.permissions import GoalPermission
from goals.serializers import GoalSerializer, GoalWithUserSerializer


class GoalCreateView(generics.CreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalListView(generics.ListAPIView):
    serializer_class = GoalWithUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['title', 'description']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Goal.objects.filter(
            category__board__participants__user=self.request.user,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalWithUserSerializer
    permission_classes = [GoalPermission]
    queryset = Goal.objects.exclude(status=Goal.Status.archived)

    def perform_destroy(self, instance: Goal) -> None:
        instance.status = Goal.Status.archived
        instance.save()
