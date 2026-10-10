from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from .forms import ArticleForm, ModerationForm
from django.db import transaction
from django.contrib.auth.models import Group
from accounts.models import AuthorProfile
from interactions.forms import CommentForm
from django.db.models import Q, Count
from .models import Article, ModerationRecord, Category, Tag
from django.core.cache import cache
from django.core.exceptions import ValidationError
from .services import moderate_article
from django.db.models import Prefetch
from core.pagination import render_paginated
from core.cache_utils import cached_list

@login_required
@permission_required("articles.add_article", raise_exception=True)
def create_article_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()

            return redirect("my_articles")
    
    else:
        form = ArticleForm()
    
    return render(request, "create_article.html", {"form": form})

@login_required
@permission_required("articles.view_article", raise_exception=True)
def my_articles_view(request):
    articles = Article.objects.filter(author=request.user).prefetch_related(Prefetch("moderation_records", queryset=ModerationRecord.objects.select_related("moderator").order_by("-created_at", "-pk"), to_attr="review_history")).order_by("-created_at", "-pk")
    return render_paginated(request, "my_articles.html", articles)

@login_required
@permission_required("articles.change_article", raise_exception=True)
@transaction.atomic
def edit_my_article_view(request, pk):
    article = get_object_or_404(Article.objects.select_for_update(), pk=pk, author=request.user)

    if article.status not in (Article.Status.DRAFT, Article.Status.REJECTED):
        return HttpResponseForbidden("Эту статью нельзя редактировать")

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)

        if form.is_valid():
            form.save()
            return redirect("my_articles")
    else:
        form = ArticleForm(instance=article)

    return render(request, "edit_my_article.html", {"form": form, "article": article})

@login_required
@permission_required("articles.change_article", raise_exception=True)
@transaction.atomic
def submit_article_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    article = get_object_or_404(Article.objects.select_for_update(), pk=pk, author=request.user)

    if article.status not in (Article.Status.DRAFT, Article.Status.REJECTED):
        return HttpResponseForbidden("Статью нельзя отправить на модерацию")

    article.status = Article.Status.SUBMITTED
    article.submitted_at = timezone.now()
    article.save(update_fields=["status", "submitted_at", "updated_at"])

    return redirect("my_articles")


@login_required
def moderate_article_view(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("У вас нет доступа")

    article = get_object_or_404(Article.objects.select_related("author").prefetch_related("categories", "tags"), pk=pk, status=Article.Status.SUBMITTED)
    form = ModerationForm(request.POST if request.method == "POST" else None)
    response_status = 200

    if request.method == "POST" and form.is_valid():
        try:
            moderate_article(article_id=article.pk, moderator=request.user, decision=form.cleaned_data["decision"], comment=form.cleaned_data["comment"])
        except ValidationError as exc:
            form.add_error(None, exc)
            response_status = 409
        else:
            return redirect("moderation_queue")

    return render(request, "moderate_article.html", {"article": article, "form": form}, status=response_status)

@login_required
def moderation_queue_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("У вас нет доступа")
    
    articles = Article.objects.filter(status=Article.Status.SUBMITTED).select_related("author").order_by("submitted_at", "pk")
    
    return render_paginated(request, "moderation_queue.html", articles)


@login_required
def become_author_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    authors_group = Group.objects.get(name="Authors")
    request.user.groups.add(authors_group)

    AuthorProfile.objects.get_or_create(user=request.user)

    return redirect("profile")

@login_required
@permission_required("articles.delete_article", raise_exception=True)
def delete_article_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    article = get_object_or_404(Article, pk=pk, author=request.user)
    article.delete()

    return redirect("my_articles")


def article_list_view(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")
    tag_slug = request.GET.get("tag", "")
    
    articles = Article.objects.filter(status=Article.Status.PUBLISHED).select_related("author").prefetch_related(Prefetch("categories", queryset=Category.objects.order_by("pk")), "tags")
    if query:
        articles = articles.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query)
        )
    
    if category_slug:
        articles = articles.filter(categories__slug=category_slug)
    
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)

    articles = articles.annotate(
        likes_count=Count("likes", distinct=True),
        comments_count=Count("comments", distinct=True),
    )
    articles = articles.distinct().order_by("-published_at")
    categories = cached_list("article_categories", Category.objects.order_by("name"))
    tags = cached_list("article_tags", Tag.objects.order_by("name"))

    return render_paginated(request, "article_list.html", articles, context={"categories": categories, "tags": tags, "query": query, "selected_category": category_slug, "selected_tag": tag_slug})


def article_detail_view(request, slug):
    article = get_object_or_404(Article.objects.select_related("author").prefetch_related("categories", "tags"), slug=slug, status=Article.Status.PUBLISHED)
    comments = article.comments.select_related("user").order_by("-created_at", "-pk")

    is_liked = False
    is_bookmarked = False

    if request.user.is_authenticated:
        is_liked = article.likes.filter(user=request.user).exists()
        is_bookmarked = article.bookmarks.filter(user=request.user).exists()

    return render_paginated(request, "article_detail.html", comments, name="comments", per_page=20, context={"article": article, "comment_form": CommentForm(), "is_liked": is_liked, "is_bookmarked": is_bookmarked})

