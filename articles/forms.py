from .models import Article, ModerationRecord
from django import forms


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'summary', 'content', 'cover_image', 'categories', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Как технологии меняют образование'}),
            'slug': forms.TextInput(attrs={'placeholder': 'kak-tehnologii-menyayut-obrazovanie'}),
            'summary': forms.Textarea(attrs={'placeholder': 'Коротко опишите статью в 1–2 предложениях…', 'rows': 4}),
            'content': forms.Textarea(attrs={'placeholder': 'Начните писать статью…', 'rows': 14}),
            'cover_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

class ModerationForm(forms.ModelForm):
    decision = forms.ChoiceField(label="Решение", choices=[(ModerationRecord.Decision.PUBLISHED, "Опубликовать"), (ModerationRecord.Decision.REJECTED, "Отклонить")])

    class Meta:
        model = ModerationRecord
        fields = ["decision", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"placeholder": "Комментарий для автора (необязательно)…", "rows": 5})}