# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission


class HasTeacherRolePermission(BasePermission):
    """
    Custom permissions to allow get chats, if the teacher is the current user.
    """
    def has_permission(self, request, view):
        try:
            role = request.query_params.get('role')
            return not (role == 'teacher' and not request.user.is_teacher)
        except AttributeError:
            return False
