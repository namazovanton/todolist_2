from rest_framework import generics, permissions, filters
from django.db import transaction
from goals.models import GoalCategory, Goal
from goals.permissions import GoalCategoryPermission
from goals.serializers import GoalCategorySerializer, GoalCategoryWithUserSerializer


class CategoryCreateView(generics.CreateAPIView):
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryListView(generics.ListAPIView):
    serializer_class = GoalCategoryWithUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_field = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(board__participants__user=self.request.user).exclude(is_deleted=True)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalCategoryWithUserSerializer
    permission_classes = [GoalCategoryPermission]
    queryset = GoalCategory.objects.exclude(is_deleted=True)

    def perform_destroy(self, instance: GoalCategory):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goal_set.update(status=Goal.Status.archived)
