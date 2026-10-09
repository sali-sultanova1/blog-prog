from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

class UsernameOrEmailLoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя или email")
 
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'bio', 'avatar']
