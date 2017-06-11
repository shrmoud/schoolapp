# -*- coding: utf-8 -*-
from rest_framework import permissions


class AuthPermissions(permissions.BasePermission):
    """
    Custom permissions to allow users to use the auth API.
    """
    def has_permission(self, request, view):
        try:
            if view.action == 'login':
                return True
            elif view.action == 'logout' and request.user.is_authenticated():
                return True
        except AttributeError:
            return False

        return False
