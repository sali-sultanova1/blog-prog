from django.db.models import Q, Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from interactions.models import Like, Bookmark
from .models import Article
from .serializers import ArticleSerializer
from .api_permissions import ArticleAPIPermission
from .filters import ArticleFilter


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [ArticleAPIPermission]
    filterset_class = ArticleFilter
    search_fields = ["title", "summary", "content", "author__username"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at"]

    def get_queryset(self):
        queryset = Article.objects.select_related("author").prefetch_related("categories", "tags").annotate(likes_count=Count("likes", distinct=True), comments_count=Count("comments", distinct=True))

        if self.action in ("list", "like", "bookmark"):
            return queryset.filter(status=Article.Status.PUBLISHED)

        if self.action == "retrieve":
            if self.request.user.is_authenticated:
                return queryset.filter(Q(status=Article.Status.PUBLISHED) | Q(author=self.request.user))
            return queryset.filter(status=Article.Status.PUBLISHED)

        if self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)

        return queryset.none()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, status=Article.Status.DRAFT)

    def perform_update(self, serializer):
        article = self.get_object()

        if article.status not in (Article.Status.DRAFT, Article.Status.REJECTED):
            raise PermissionDenied("Эту статью нельзя редактировать.")

        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        article = self.get_object()
        like, created = Like.objects.get_or_create(article=article, user=request.user)

        if created:
            liked = True
        else:
            like.delete()
            liked = False

        return Response({"liked": liked, "likes_count": article.likes.count()})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        article = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(article=article, user=request.user)

        if created:
            bookmarked = True
        else:
            bookmark.delete()
            bookmarked = False

        return Response({"bookmarked": bookmarked})