from rest_framework.permissions import BasePermission, SAFE_METHODS


class ArticleAPIPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if view.action == "create":
            return request.user.has_perm("articles.add_article")

        if view.action in ("update", "partial_update"):
            return request.user.has_perm("articles.change_article")

        if view.action == "destroy":
            return request.user.has_perm("articles.delete_article")

        if view.action in ("like", "bookmark"):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if view.action in ("like", "bookmark"):
            return True

        return obj.author == request.user