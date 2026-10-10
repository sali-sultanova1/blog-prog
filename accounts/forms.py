from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Придумайте имя пользователя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Придумайте пароль'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите пароль'})

class UsernameOrEmailLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя или email',
        widget=forms.TextInput(attrs={'placeholder': 'username или name@example.com'})
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'autocomplete': 'current-password'})
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Расскажите немного о себе…', 'rows': 5}),
            'avatar': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }