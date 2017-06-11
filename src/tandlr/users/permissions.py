# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Custom permissions to allow only superuser
    """
    def has_permission(self, request, view):
        try:
            return request.user.is_superuser
        except AttributeError:
            return False
