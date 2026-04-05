from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение:
    - GET (чтение) — разрешено всем
    - PUT/PATCH/DELETE (изменение/удаление) — только автору поста
    """

    def has_object_permission(self, request, view, obj):
        # Безопасные методы (GET, HEAD, OPTIONS) — разрешены всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для остальных методов — проверяем, что пользователь = автор
        return obj.author == request.user
