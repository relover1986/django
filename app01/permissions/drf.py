"""DRF 权限类"""
from rest_framework.permissions import BasePermission


class IsAuthenticatedSession(BasePermission):
    """基于 session 的登录校验"""
    def has_permission(self, request, view):
        return bool(request.session.get('info'))


class IsStaffOrAdmin(BasePermission):
    """员工或管理员权限"""
    def has_permission(self, request, view):
        info = request.session.get('info')
        if not info:
            return False
        role = info.get('role', '')
        return bool(role)
