from django.shortcuts import render, redirect
from .forms import ArticleForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

@login_required
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
def my_articles_view(request):
    articles = Article.objects.filter(author = request.user).order_by("-created_at")
    return render(request, "my_articles.html", {"articles": articles})

@login_required
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
