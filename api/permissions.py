from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - GET/HEAD/OPTIONS requests allowed for anyone (safe methods)
    - POST/PUT/PATCH/DELETE only for admin users
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsProductOwnerOrAdmin(permissions.BasePermission):
    """Object-level permission for product owners or admins"""
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for owner or admin
        return obj.owner == request.user or request.user.is_staff

class IsOrderOwnerOrAdmin(permissions.BasePermission):
    """Check if user is order owner or admin"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.initiator == request.user or request.user.is_staff