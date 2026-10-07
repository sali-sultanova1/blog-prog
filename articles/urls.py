from django.urls import path
from .views import create_article_view 

urlpatterns = [
    path("create/", create_article_view, name="create_article"),

]