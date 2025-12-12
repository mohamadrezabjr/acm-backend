from rest_framework.permissions import BasePermission

class IsCreator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_creator

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin
