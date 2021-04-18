from rest_framework import permissions


class IsAdminOrIsOwnerOrSingup(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.method == 'POST'\
                or request.user.is_authenticated:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if obj == request.user or request.user.is_staff is True:
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS or request.user.is_staff)


class IsAdminOrCreateOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS or request.method == 'POST' or request.user.is_staff)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user_id == request.user.id


class IsOwnerOrCreateOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True

        return obj.user_id == request.user.id


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


# Only for RecipeIngredients and Step ownership check
class IsOwnerRecipeOrCreateOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True
        return obj.recipe.user_id == request.user.id
