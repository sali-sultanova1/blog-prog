from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from interactions.models import Like, Bookmark
from .models import Article, Category, Tag
from .serializers import ArticleSerializer, CategorySerializer, TagSerializer
from .api_permissions import ArticleAPIPermission, AdminWritePermission
from .filters import ArticleFilter
from .services import unpublish_article

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AdminWritePermission]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [AdminWritePermission]
    search_fields = ["name"]
    ordering_fields = ["name"]

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [ArticleAPIPermission]
    filterset_class = ArticleFilter
    search_fields = ["title", "summary", "content", "author__username", "tags__name"]
    ordering_fields = ["published_at", "created_at", "updated_at", "title", "id"]
    ordering = ["-published_at", "-pk"]

    def get_queryset(self):
        queryset = Article.objects.select_related("author").prefetch_related("categories", "tags").annotate(likes_count=Count("likes", distinct=True), comments_count=Count("comments", distinct=True))

        if self.action == "mine":
            return queryset.filter(author=self.request.user) if self.request.user.is_authenticated else queryset.none()

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

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        get_object_or_404(Article.objects.select_for_update(), pk=kwargs["pk"], author=request.user)
        return super().update(request, *args, **kwargs)

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

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated], ordering=["-created_at", "-pk"])
    def mine(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)

        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unpublish(self, request, pk=None):
        try:
            article = unpublish_article(article_id=pk, actor=request.user)
        except DjangoValidationError as exc:
            return Response({"detail": " ".join(exc.messages)}, status=409)

        return Response(self.get_serializer(article).data)