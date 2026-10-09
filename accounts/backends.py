from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()

        if username is None or password is None:
            return None

        user = User.objects.filter(email__iexact=username).first()

        if user is None:
            user = User.objects.filter(username=username).first()

        if user is None:
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None