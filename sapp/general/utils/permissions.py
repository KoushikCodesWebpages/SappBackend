from rest_framework.permissions import BasePermission

class IsOfficeAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'so_admin' 

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student' 

class IsFaculty(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'faculty' 
