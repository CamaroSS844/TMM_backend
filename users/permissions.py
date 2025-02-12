from rest_framework.permissions import BasePermission

class IsCemeteryWorker(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'basic_worker'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'