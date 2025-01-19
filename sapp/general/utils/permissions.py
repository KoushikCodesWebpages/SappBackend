from rest_framework.permissions import BasePermission

class IsOfficeAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'office_admin' and request.user.is_verified

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student' and request.user.is_verified

class IsFaculty(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'faculty' and request.user.is_verified
