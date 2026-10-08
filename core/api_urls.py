from rest_framework.routers import DefaultRouter

from articles.api_views import ArticleViewSet
from interactions.api_views import CommentViewSet
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from articles.api_views import ArticleViewSet
from interactions.api_views import CommentViewSet

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="api-article")
router.register("comments", CommentViewSet, basename="api-comment")


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += router.urls