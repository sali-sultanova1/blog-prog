from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from .forms import ArticleForm, ModerationForm
from .models import Article, ModerationRecord
from django.db import transaction
from django.contrib.auth.models import Group

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
    articles = Article.objects.filter(author = request.user).order_by("-created_at")
    return render(request, "my_articles.html", {"articles": articles})

@login_required
@permission_required("articles.change_article", raise_exception=True)
def edit_my_article_view(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if article.status not in (Article.Status.DRAFT, Article.Status.REJECTED):
        return HttpResponseForbidden("Эту статью нельзя редактировать")

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)

        if form.is_valid():
            form.save()

            return redirect("my_articles")
    
    else:
        form = ArticleForm(instance=article)
    
    return render(request, "edit_my_article.html", {"form": form, "article": article})


@login_required
@permission_required("articles.change_article", raise_exception=True)
def submit_article_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    article = get_object_or_404(Article, pk=pk, author=request.user)

    if article.status not in (Article.Status.DRAFT, Article.Status.REJECTED):
        return HttpResponseForbidden("Статью нельзя отправить на модерацию")
    
    article.status = Article.Status.SUBMITTED
    article.submitted_at = timezone.now()
    article.save()

    return redirect("my_articles")


@login_required
def moderate_article_view(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("У вас нет доступа")
    
    article = get_object_or_404(Article, pk=pk, status=Article.Status.SUBMITTED)

    if request.method == 'POST':
        form = ModerationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                moderation = form.save(commit=False)

                moderation.article = article
                moderation.moderator = request.user

                if moderation.decision == ModerationRecord.Decision.PUBLISHED:
                    article.status = Article.Status.PUBLISHED
                    article.published_at = timezone.now()
                else:
                    article.status = Article.Status.REJECTED

                article.save()
                moderation.save()


            return redirect("moderation_queue")
    
    else:
        form = ModerationForm()
    
    return render(request, "moderate_article.html", {"form": form, "article": article})


@login_required
def moderation_queue_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("У вас нет доступа")
    
    articles = Article.objects.filter(status=Article.Status.SUBMITTED).order_by("submitted_at")
    
    return render(request, "moderation_queue.html", {"articles": articles})


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