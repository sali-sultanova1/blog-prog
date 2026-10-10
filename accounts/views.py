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
from .models import AuthorProfile, CustomUser
from django.http import Http404
from core.pagination import render_paginated
import logging
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from core.cache_utils import CACHE_ERRORS, delete_cache_safely
from .forms import ProfileForm, RegisterForm

logger = logging.getLogger(__name__)

PENDING_REGISTRATION_TIMEOUT = 30 * 60

def register_view(request):
    form = RegisterForm(request.POST if request.method == "POST" else None)

    if request.method == "POST" and form.is_valid():
        token = secrets.token_urlsafe(32)
        cache_key = f"pending_registration:{token}"
        pending_user = {"username": form.cleaned_data["username"], "email": form.cleaned_data["email"], "password_hash": make_password(form.cleaned_data["password1"])}

        try:
            cache.set(cache_key, pending_user, timeout=PENDING_REGISTRATION_TIMEOUT)
        except CACHE_ERRORS:
            logger.exception("Не удалось сохранить ожидающую регистрацию.")
            form.add_error(None, "Регистрация временно недоступна. Попробуйте немного позже.")
            return render(request, "register.html", {"form": form}, status=503)

        try:
            send_verification_email(request, pending_user["username"], pending_user["email"], token)
        except Exception:
            logger.exception("Не удалось отправить письмо подтверждения.")
            delete_cache_safely(cache_key)
            form.add_error(None, "Не удалось отправить письмо. Попробуйте зарегистрироваться ещё раз.")
            return render(request, "register.html", {"form": form}, status=503)

        return render(request, "verification_sent.html", {"email": pending_user["email"]})

    return render(request, "register.html", {"form": form})

@login_required
def author_profile_view(request, username):
    author = get_object_or_404(CustomUser, username=username)
    articles = Article.objects.filter(author=author, status=Article.Status.PUBLISHED).order_by("-published_at", "-pk")
    author_profile = AuthorProfile.objects.select_related("user").filter(user=author).first()

    if author_profile is None:
        if not (author.has_perm("articles.add_article") or articles.exists()):
            raise Http404("Автор не найден.")

        author_profile = AuthorProfile(user=author)

    stats = articles.aggregate(total_likes=Count("likes", distinct=True), total_comments=Count("comments", distinct=True))
    
    return render_paginated(request, "author_profile.html", articles, context={"author_profile": author_profile, "stats": stats, "articles_count": articles.count()})

@login_required
def profile_view(request):
    return render(request, "profile.html")

@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "edit_profile.html", {"form": form})

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

    try:
        pending_user = cache.get(cache_key)
    except CACHE_ERRORS:
        logger.exception("Не удалось прочитать ожидающую регистрацию.")
        return HttpResponse("Подтверждение временно недоступно. Попробуйте открыть ссылку позже.", status=503, content_type="text/plain; charset=utf-8")

    if pending_user is None:
        return render(request, "verification_invalid.html", status=400)

    try:
        with transaction.atomic():
            user = CustomUser(username=pending_user["username"], email=pending_user["email"].strip().lower(), password=pending_user["password_hash"])
            user.full_clean()
            user.save()
    except (ValidationError, IntegrityError):
        delete_cache_safely(cache_key)
        return render(request, "verification_invalid.html", status=400)

    delete_cache_safely(cache_key)
    messages.success(request, "Email подтверждён. Аккаунт создан — теперь вы можете войти.")

    return redirect("login")