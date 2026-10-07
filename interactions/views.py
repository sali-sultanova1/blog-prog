from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from articles.models import Article
from .forms import CommentForm
from .models import Comment, Like, Bookmark

@login_required
def add_comment_view(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)
        
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.article = article
        comment.save()

    return redirect("article_detail", slug=article.slug)

@login_required
def edit_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
   
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()

            return redirect("article_detail", slug=comment.article.slug,)
    
    else:
        form = CommentForm(instance=comment)
    
    return render(request, "edit_comment.html", {"form": form, "comment": comment})


@login_required
def delete_comment_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    slug = comment.article.slug
    comment.delete()

    return redirect("article_detail", slug=slug)

@login_required
def toggle_like_view(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)
    like = Like.objects.filter(article=article, user=request.user).first()

    if like:
        like.delete()
    else:
        Like.objects.create(article=article, user=request.user)
    
    return redirect("article_detail", slug=slug)

@login_required
def toggle_bookmark_view(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)
    bookmark = Bookmark.objects.filter(article=article, user=request.user).first()

    if bookmark:
        bookmark.delete()
    else:
        Bookmark.objects.create(article=article, user=request.user)
    
    return redirect("article_detail", slug=slug)
