from rest_framework import permissions
    
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.roles.filter(role__in=["ADMIN", "SUPER_ADMIN"]).exists()

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admins to modify, but read-only for others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.roles.filter(role__in=["ADMIN", "SUPER_ADMIN"]).exists()
