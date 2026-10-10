from django.urls import path
from .views import register_view, profile_view, edit_profile_view, author_profile_view, verify_email_view
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UsernameOrEmailLoginForm

urlpatterns = [
    path('register/', register_view, name="register"),
    path("verify-email/<str:token>/", verify_email_view, name="verify_email"),
    path('login/', LoginView.as_view(template_name="login.html", authentication_form=UsernameOrEmailLoginForm), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile_view, name="edit_profile"),
    path("authors/<str:username>/", author_profile_view, name="author_profile"),


]