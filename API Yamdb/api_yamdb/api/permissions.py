from rest_framework.permissions import SAFE_METHODS, BasePermission


class ModeratorOrReadOnly(BasePermission):
    """Все права модератору или только чтение."""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_moderator)


class AuthorOrReadOnly(BasePermission):
    """Все права автору или только чтение."""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author)


class AdminOrSuperUser(BasePermission):
    """Предоставляет права на осуществление запросов
    только суперпользователю, админу."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_admin)
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_admin)


class IsAdminOrReadOnly(BasePermission):
    """Разрешение для пользователей с правами администратора или на чтение."""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser)))
