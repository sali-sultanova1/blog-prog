from rest_framework.routers import DefaultRouter

from articles.api_views import ArticleViewSet
from interactions.api_views import CommentViewSet


router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="api-article",)
router.register("comments", CommentViewSet, basename="api-comment",)


urlpatterns = router.urls