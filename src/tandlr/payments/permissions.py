# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission


class TeacherPaymentInformationPermission(BasePermission):
    """
    Custom permissions to allow students to get only their own class extensions
    """
    def has_permission(self, request, view):
        try:
            return request.user.is_teacher
        except AttributeError:
            return False
