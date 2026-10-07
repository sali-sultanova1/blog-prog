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