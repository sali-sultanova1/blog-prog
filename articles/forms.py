from .models import Article, ModerationRecord
from django import forms

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'summary', 'content', 'cover_image', 'categories', 'tags']

class ModerationForm(forms.ModelForm):
    class Meta:
        model = ModerationRecord
        fields = ["decision", "comment"]