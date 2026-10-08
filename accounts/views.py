from django.shortcuts import render, redirect
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {"form": form})


@login_required
def profile_view(request):
    return render(request, "profile.html")


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect("profile")
    
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, "edit_profile.html", {"form": form})

@login_required
def author_profile_view(request, username):
    author_profile = get_object_or_404(AuthorProfile, user__username=username)
    articles = Article.objects.filter(author=author_profile.user, status=Article.Status.PUBLISHED).order_by("-published_at")
    return render(request, "author_profile.html", {"author_profile": author_profile, "articles": articles})