# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission


class BalancePermission(BasePermission):
    """
    Custom permissions to allow teacher to get their balance
    """
    def has_permission(self, request, view):
        try:
            return request.user.is_teacher
        except AttributeError:
            return False
