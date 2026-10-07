from django.shortcuts import render

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
