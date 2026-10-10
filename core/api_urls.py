from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from interactions.api_views import CommentViewSet
from articles.api_views import ArticleViewSet, CategoryViewSet, TagViewSet
from core.rate_limits import limit_posts

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="api-article")
router.register("categories", CategoryViewSet, basename="api-category")
router.register("tags", TagViewSet, basename="api-tag")
router.register("comments", CommentViewSet, basename="api-comment")

urlpatterns = [
    path("token/", limit_posts(scope="jwt-login", limit=20, window=300)(TokenObtainPairView.as_view()), name="token_obtain_pair"),
    path("token/refresh/", limit_posts(scope="jwt-refresh", limit=60, window=300)(TokenRefreshView.as_view()), name="token_refresh"),
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs",),
]

urlpatterns += router.urls