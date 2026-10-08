from rest_framework import viewsets

from .models import Comment
from .serializers import CommentSerializer
from .api_permissions import CommentAPIPermission


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [CommentAPIPermission]
    filterset_fields = ["article"]
    search_fields = ["content", "user__username"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    queryset = (
        Comment.objects
        .select_related("user", "article")
        .order_by("-created_at")
    )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )