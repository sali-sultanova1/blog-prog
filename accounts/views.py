import secrets
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from articles.models import Article
from .forms import ProfileForm, RegisterForm
from .models import AuthorProfile, CustomUser

PENDING_REGISTRATION_TIMEOUT = 30 * 60

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            token = secrets.token_urlsafe(32)
            cache_key = f"pending_registration:{token}"
            pending_user = {"username": form.cleaned_data["username"], "email": form.cleaned_data["email"], "password_hash": make_password(form.cleaned_data["password1"])}

            cache.set(cache_key, pending_user, timeout=PENDING_REGISTRATION_TIMEOUT)

            try:
                send_verification_email(request, pending_user["username"], pending_user["email"], token)
            except Exception:
                cache.delete(cache_key)
                messages.error(request, "Не удалось отправить письмо. Попробуйте зарегистрироваться ещё раз.")
                return render(request, "register.html", {"form": form}, status=503)

            return render(request, "verification_sent.html", {"email": pending_user["email"]})
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


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
    stats = articles.aggregate(
        total_likes=Count("likes", distinct=True),
        total_comments=Count("comments", distinct=True),
    )

    articles_count = articles.count()
    return render(request, "author_profile.html", {"author_profile": author_profile, "articles": articles, "stats": stats, "articles_count": articles_count,})



def send_verification_email(request, username, email, token):
    verification_url = request.build_absolute_uri(reverse("verify_email", kwargs={"token": token}))

    send_mail(
        subject="Подтверждение email — News Blog",
        message=f"Здравствуйте, {username}!\n\nДля завершения регистрации подтвердите адрес электронной почты:\n\n{verification_url}\n\nСсылка действительна 30 минут.\n\nЕсли вы не регистрировались на News Blog, просто проигнорируйте это письмо.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def verify_email_view(request, token):
    cache_key = f"pending_registration:{token}"
    pending_user = cache.get(cache_key)

    if pending_user is None:
        return render(request, "verification_invalid.html", status=400)

    if CustomUser.objects.filter(username=pending_user["username"]).exists():
        cache.delete(cache_key)
        return render(request, "verification_invalid.html", status=400)

    if CustomUser.objects.filter(email__iexact=pending_user["email"]).exists():
        cache.delete(cache_key)
        return render(request, "verification_invalid.html", status=400)

    try:
        with transaction.atomic():
            user = CustomUser(username=pending_user["username"], email=pending_user["email"], password=pending_user["password_hash"])
            user.save()
    except IntegrityError:
        cache.delete(cache_key)
        return render(request, "verification_invalid.html", status=400)

    cache.delete(cache_key)
    messages.success(request, "Email подтверждён. Аккаунт создан — теперь вы можете войти.")
    return redirect("login")