from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from articles.models import Article
from .forms import ProfileForm, RegisterForm
from .models import AuthorProfile, CustomUser
from .tokens import email_verification_token

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            try:
                send_verification_email(request, user)
            except Exception:
                user.delete()
                messages.error(
                    request,
                    "Не удалось отправить письмо. Попробуйте зарегистрироваться ещё раз.",
                )
                return render(request, "register.html", {"form": form}, status=503)

            return render(request, "verification_sent.html", {"email": user.email},)
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



def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_url = request.build_absolute_uri(
        reverse(
            "verify_email",
            kwargs={"uidb64": uid, "token": token},
        )
    )

    send_mail(
        subject="Подтверждение email — News Blog",
        message=(
            f"Здравствуйте, {user.username}!\n\n"
            "Для завершения регистрации подтвердите адрес электронной почты:\n\n"
            f"{verification_url}\n\n"
            "Если вы не регистрировались на News Blog, просто проигнорируйте это письмо."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_email_view(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])

        messages.success(request, "Email подтверждён. Теперь вы можете войти.")
        return redirect("login")

    return render(request, "verification_invalid.html", status=400)