from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from articles.api_views import ArticleViewSet
from interactions.api_views import CommentViewSet

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="api-article")
router.register("comments", CommentViewSet, basename="api-comment")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs",),
]

urlpatterns += router.urls