from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated:
                return user.groups.filter(name = 'Admin').exists()
        return False

class IsAuthenticatedLoggin(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if user.is_authenticated:
                return user.logged_in
        return False
